from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import yaml

CONFIG_FILE_NAME = "fhirscripts.multiig.config.yaml"
DEFAULT_IGS_ROOT = "igs"


@dataclass(frozen=True)
class IGTarget:
    name: str
    path: Path


@dataclass(frozen=True)
class MultiIGProject:
    repo_root: Path
    targets: dict[str, IGTarget]
    base_igs: list[str]


class SelectionError(Exception):
    pass


def discover_project(start_dir: Path | None = None) -> MultiIGProject | None:
    cwd = (start_dir or Path.cwd()).resolve()

    for base in [cwd, *cwd.parents]:
        if (cfg_path := base / CONFIG_FILE_NAME).exists():
            return _project_from_config(base, cfg_path)

        if project := _project_from_convention(base):
            return project

    return None


def select_targets(
    ig: list[str] | None,
    select_all: bool,
    cwd: Path | None = None,
) -> list[IGTarget]:
    current_dir = (cwd or Path.cwd()).resolve()
    requested = [name.strip() for name in (ig or []) if name.strip()]
    project = discover_project(current_dir)

    if project is None:
        if requested or select_all:
            raise SelectionError(
                "No multi-IG repository detected. Either run inside an IG directory or add "
                f"'{CONFIG_FILE_NAME}' in the repository root."
            )

        return []

    target_names = sorted(project.targets.keys())

    if requested:
        unknown = [name for name in requested if name not in project.targets]
        if unknown:
            raise SelectionError(
                "Unknown IG name(s): {}. Valid IG names: {}".format(
                    ", ".join(unknown), ", ".join(target_names)
                )
            )

        # Keep user-defined order while removing duplicates.
        unique_requested = list(dict.fromkeys(requested))
        return [project.targets[name] for name in unique_requested]

    if select_all:
        return [project.targets[name] for name in target_names]

    auto_detected = _detect_target_from_cwd(project, current_dir)
    if auto_detected:
        return [auto_detected]

    raise SelectionError(
        "Unable to determine a target IG from the current directory. "
        "Use '--ig <name>' (repeatable) or '--all'. "
        "Valid IG names: {}".format(", ".join(target_names))
    )


def select_build_targets(
    ig: list[str] | None,
    select_all: bool,
    cwd: Path | None = None,
) -> list[IGTarget]:
    current_dir = (cwd or Path.cwd()).resolve()
    selected = select_targets(ig=ig, select_all=select_all, cwd=current_dir)
    project = discover_project(current_dir)

    if project is None or len(project.base_igs) == 0:
        return selected

    return _prepend_base_igs(selected, project)


def _project_from_config(repo_root: Path, config_path: Path) -> MultiIGProject:
    raw = yaml.safe_load(config_path.read_text("utf-8")) or {}
    igs_root = raw.get("igsRoot", DEFAULT_IGS_ROOT)
    if not isinstance(igs_root, str) or not igs_root.strip():
        raise SelectionError(
            f"Invalid '{CONFIG_FILE_NAME}': field 'igsRoot' must be a non-empty string"
        )

    ig_entries = raw.get("igs")
    if ig_entries is None:
        return _project_from_root_only_config(repo_root, raw, igs_root)

    if not isinstance(ig_entries, dict):
        raise SelectionError(
            f"Invalid '{CONFIG_FILE_NAME}': field 'igs' must be a mapping if provided"
        )

    if len(ig_entries) == 0:
        return _project_from_root_only_config(repo_root, raw, igs_root)

    targets: dict[str, IGTarget] = {}

    for ig_name, ig_conf in ig_entries.items():
        if not isinstance(ig_name, str) or not ig_name:
            raise SelectionError(
                f"Invalid '{CONFIG_FILE_NAME}': IG names must be non-empty strings"
            )

        if not isinstance(ig_conf, dict):
            raise SelectionError(
                f"Invalid '{CONFIG_FILE_NAME}': IG entry '{ig_name}' must be a mapping"
            )

        rel_path = ig_conf.get("path")
        if not isinstance(rel_path, str) or not rel_path.strip():
            raise SelectionError(
                f"Invalid '{CONFIG_FILE_NAME}': IG '{ig_name}' requires a non-empty 'path'"
            )

        abs_path = (repo_root / Path(rel_path)).resolve()
        if not abs_path.exists() or not abs_path.is_dir():
            raise SelectionError(
                f"IG '{ig_name}' points to missing directory: {abs_path}"
            )

        targets[ig_name] = IGTarget(name=ig_name, path=abs_path)

    return MultiIGProject(
        repo_root=repo_root,
        targets=targets,
        base_igs=_parse_base_igs(raw, targets),
    )


def _project_from_root_only_config(
    repo_root: Path, raw: dict, igs_root: str
) -> MultiIGProject:
    root = (repo_root / Path(igs_root)).resolve()
    if not root.exists() or not root.is_dir():
        raise SelectionError(
            f"Invalid '{CONFIG_FILE_NAME}': igsRoot points to missing directory: {root}"
        )

    targets = {
        candidate.name: IGTarget(name=candidate.name, path=candidate.resolve())
        for candidate in sorted(root.iterdir())
        if candidate.is_dir()
    }

    if len(targets) == 0:
        raise SelectionError(
            f"Invalid '{CONFIG_FILE_NAME}': no IG directories found below {root}"
        )

    return MultiIGProject(
        repo_root=repo_root,
        targets=targets,
        base_igs=_parse_base_igs(raw, targets),
    )


def _project_from_convention(repo_root: Path) -> MultiIGProject | None:
    igs_root = repo_root / DEFAULT_IGS_ROOT
    if not igs_root.exists() or not igs_root.is_dir():
        return None

    targets: dict[str, IGTarget] = {}

    for candidate in sorted(igs_root.iterdir()):
        if not candidate.is_dir():
            continue

        # A directory is treated as IG if it has common IG markers.
        if not (
            (candidate / "sushi-config.yaml").exists()
            or (candidate / "publication-request.json").exists()
        ):
            continue

        targets[candidate.name] = IGTarget(
            name=candidate.name, path=candidate.resolve()
        )

    if len(targets) == 0:
        return None

    return MultiIGProject(repo_root=repo_root, targets=targets, base_igs=[])


def _parse_base_igs(raw: dict, targets: dict[str, IGTarget]) -> list[str]:
    base = raw.get("baseIG", [])

    if base is None:
        return []

    if not isinstance(base, list):
        raise SelectionError(
            f"Invalid '{CONFIG_FILE_NAME}': field 'baseIG' must be a list if provided"
        )

    target_names = sorted(targets.keys())
    normalized: list[str] = []
    for entry in base:
        if not isinstance(entry, str) or not entry.strip():
            raise SelectionError(
                f"Invalid '{CONFIG_FILE_NAME}': entries in 'baseIG' must be non-empty strings"
            )

        ig_name = entry.strip()
        if ig_name not in targets:
            raise SelectionError(
                "Invalid '{}': baseIG contains unknown IG '{}'. Valid IG names: {}".format(
                    CONFIG_FILE_NAME,
                    ig_name,
                    ", ".join(target_names),
                )
            )

        if ig_name not in normalized:
            normalized.append(ig_name)

    return normalized


def _prepend_base_igs(
    selected: list[IGTarget], project: MultiIGProject
) -> list[IGTarget]:
    if len(selected) == 0:
        return selected

    selected_names = [target.name for target in selected]
    base = project.base_igs
    base_set = set(base)

    if any(name not in base_set for name in selected_names):
        base_prefix = base
    else:
        max_idx = max(base.index(name) for name in selected_names)
        base_prefix = base[: max_idx + 1]

    ordered_names = list(dict.fromkeys([*base_prefix, *selected_names]))
    return [project.targets[name] for name in ordered_names]


def _detect_target_from_cwd(project: MultiIGProject, cwd: Path) -> IGTarget | None:
    matches = [
        target
        for target in project.targets.values()
        if cwd == target.path or cwd.is_relative_to(target.path)
    ]

    if len(matches) == 0:
        return None

    # Prefer the deepest matching path if nested structures exist.
    return max(matches, key=lambda target: len(target.path.parts))


@contextmanager
def working_directory(path: Path):
    previous = Path.cwd()
    try:
        Path(path).resolve()
        import os

        os.chdir(path)
        yield
    finally:
        import os

        os.chdir(previous)
