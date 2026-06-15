import subprocess
import sys
from argparse import REMAINDER
from argparse import ArgumentParser
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import ValidationError

from . import log
from .exception import SelectionError
from .models.multiig_config import MultiIGConfig

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


def discover_project(start_dir: Path | None = None) -> MultiIGProject | None:
    """Discover a multi-IG repository starting from current directory and parents."""
    cwd = (start_dir or Path.cwd()).expanduser().resolve()

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
    """Resolve IG targets by explicit selection, --all, or auto-detection from cwd."""
    current_dir = (cwd or Path.cwd()).expanduser().resolve()
    requested = [n for name in (ig or []) if (n := name.strip())]
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

        # Deduplicate while preserving the user-defined order.
        # (dict.fromkeys keeps first-seen entries; set() would lose order)
        seen: set[str] = set()
        unique_requested = [n for n in requested if not (n in seen or seen.add(n))]
        return [project.targets[name] for name in unique_requested]

    if select_all:
        # Return a stable, sorted list – not the raw dict – so callers always
        # iterate IGs in a deterministic order regardless of insertion order.
        return [project.targets[name] for name in target_names]

    auto_detected = _detect_target_from_cwd(project, current_dir)
    if auto_detected:
        return [auto_detected]

    raise SelectionError(
        "Unable to determine a target IG from the current directory. "
        "Use '--ig <name>' (repeatable) or '--all'. "
        "Valid IG names: {}".format(", ".join(target_names))
    )


def _project_from_config(repo_root: Path, config_path: Path) -> MultiIGProject:
    """Build a project definition from explicit multi-IG configuration."""
    raw = yaml.safe_load(config_path.read_text("utf-8")) or {}
    try:
        model = MultiIGConfig.model_validate(raw)
    except ValidationError as exc:
        raise SelectionError(f"Invalid '{CONFIG_FILE_NAME}': {exc}") from exc

    ig_entries = model.igs
    if ig_entries is None:
        return _project_from_root_only_config(repo_root, model.igsRoot)

    if len(ig_entries) == 0:
        return _project_from_root_only_config(repo_root, model.igsRoot)

    targets: dict[str, IGTarget] = {}

    for ig_name, ig_conf in ig_entries.items():
        if not ig_name:
            raise SelectionError(
                f"Invalid '{CONFIG_FILE_NAME}': IG names must be non-empty strings"
            )

        abs_path = (repo_root / Path(ig_conf.path)).expanduser().resolve()
        if not abs_path.exists() or not abs_path.is_dir():
            raise SelectionError(
                f"IG '{ig_name}' points to missing directory: {abs_path}"
            )

        targets[ig_name] = IGTarget(name=ig_name, path=abs_path)

    return MultiIGProject(repo_root=repo_root, targets=targets)


def _project_from_root_only_config(repo_root: Path, igs_root: str) -> MultiIGProject:
    """Discover IG directories below the configured IG root path."""
    root = (repo_root / Path(igs_root)).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SelectionError(
            f"Invalid '{CONFIG_FILE_NAME}': igsRoot points to missing directory: {root}"
        )

    targets = {
        candidate.name: IGTarget(name=candidate.name, path=candidate.resolve())
        for candidate in root.iterdir()
        if candidate.is_dir()
    }

    if len(targets) == 0:
        raise SelectionError(
            f"Invalid '{CONFIG_FILE_NAME}': no IG directories found below {root}"
        )

    return MultiIGProject(repo_root=repo_root, targets=targets)


def _project_from_convention(repo_root: Path) -> MultiIGProject | None:
    """Discover IGs by convention in igs/<name> when no explicit config exists."""
    igs_root = repo_root / DEFAULT_IGS_ROOT
    if not igs_root.exists() or not igs_root.is_dir():
        return None

    targets: dict[str, IGTarget] = {}

    for candidate in igs_root.iterdir():
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

    return MultiIGProject(repo_root=repo_root, targets=targets)


def _detect_target_from_cwd(project: MultiIGProject, cwd: Path) -> IGTarget | None:
    """Map current working directory to the most specific matching IG target."""
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
    """Temporarily switch process working directory for command execution."""
    previous = Path.cwd()
    try:
        Path(path).resolve()
        import os

        os.chdir(path)
        yield
    finally:
        import os

        os.chdir(previous)


def setup_parser(parser: ArgumentParser, *args, **kwargs):
    parser.add_argument(
        "--ig",
        action="append",
        default=[],
        help="Target IG name(s), repeat option: 'fhirscripts multiig --ig core --ig rx build pipeline'",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run command for all IGs in the multi-IG repository",
    )
    parser.add_argument(
        "command",
        nargs=REMAINDER,
        help="fhirscripts command to run in selected IG directories",
    )


def handle_multiig(
    command: list[str],
    ig: list[str] | None = None,
    all: bool = False,
    config_path: Path | None = None,
    *args,
    **kwargs,
):
    """Execute a fhirscripts command sequentially for selected IG targets."""
    forwarded_command = command

    if len(forwarded_command) > 0 and forwarded_command[0] == "--":
        forwarded_command = forwarded_command[1:]

    if len(forwarded_command) == 0:
        raise Exception("Missing command to execute in multi-IG mode")

    if forwarded_command[0] == "multiig":
        raise Exception("Nested multi-IG mode is not supported")

    requested_igs = [name.strip() for name in (ig or []) if name and name.strip()]
    select_all = all or len(requested_igs) == 0
    targets = select_targets(ig=requested_igs, select_all=select_all)

    base_cmd = [sys.executable, "-m", "fhir_scripts"]
    if config_path is not None:
        base_cmd += ["--config", str(config_path.resolve())]

    failures: list[str] = []
    for target in targets:
        cmd = [*base_cmd, *forwarded_command]
        log.info(f"Run command in IG '{target.name}': {' '.join(forwarded_command)}")
        proc = subprocess.run(cmd, cwd=target.path, check=False)

        if proc.returncode == 0:
            log.succ(f"Command succeeded for IG '{target.name}'")
        else:
            failures.append(target.name)
            log.fail(
                f"Command failed for IG '{target.name}' (exit code {proc.returncode})"
            )

    if failures:
        raise Exception(
            "multiig execution failed for IG(s): {}".format(", ".join(failures))
        )


__doc__ = "Run any fhirscripts command for multiple IGs"
__handler__ = handle_multiig
__setup_parser__ = setup_parser
