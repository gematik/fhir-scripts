import json
from argparse import ArgumentParser
from pathlib import Path

from . import log
from .helper import confirm
from .models.config import Config, DeployConfig
from .tools import gcloud
from .types import Url

TARGET_BASE_DIR = "ig/fhir"


def setup_parser(parser: ArgumentParser, *args, **kwarsg):
    parser.add_argument("environment", help="Name of the environment")
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm all prompts with 'yes'"
    )
    parser.add_argument(
        "--promote-from",
        type=str,
        help="Promote from another environment insread of the local build directory",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Only pretend to deploy files"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--only-ig", action="store_true", help="Deploy only the IG")
    group.add_argument(
        "--only-meta", action="store_true", help="Deploy only the IG meta data"
    )
    group.add_argument(
        "--ig-registry", action="store_true", help="Deploy IG registry entries"
    )


def deploy(
    config: Config,
    environment: str,
    ig_registry: bool = False,
    only_ig: bool = False,
    only_meta: bool = False,
    yes: bool = False,
    dry_run: bool = False,
    promote_from: str | None = None,
    *args,
    **kwargs,
) -> bool:
    deploy_config = config.deploy
    if deploy_config is None:
        raise Exception("deploy configuration missing")

    if ig_registry:
        deploy_ig_registry(
            deploy_config,
            environment,
            promote_from_env=promote_from,
            dry_run=dry_run,
            confirm_yes=yes,
        )

    else:
        if only_ig:
            deploy_ig(
                deploy_config,
                environment,
                promote_from_env=promote_from,
                dry_run=dry_run,
                confirm_yes=yes,
            )

        elif only_meta:
            deploy_ig_meta(
                deploy_config,
                environment,
                promote_from_env=promote_from,
                dry_run=dry_run,
                confirm_yes=yes,
            )

        else:
            deploy_ig(
                deploy_config,
                environment,
                promote_from_env=promote_from,
                dry_run=dry_run,
                confirm_yes=yes,
            )
            deploy_ig_meta(
                deploy_config,
                environment,
                promote_from_env=promote_from,
                dry_run=dry_run,
                confirm_yes=yes,
            )

    return True


def deploy_ig_registry(
    deploy_cfg: DeployConfig,
    target_env: str,
    promote_from_env: str | None = None,
    confirm_yes: bool = False,
    dry_run: bool = False,
    *args,
    **kwargs,
):
    target_path = get_storage_path(deploy_cfg, target_env)

    if promote_from_env:
        source_path = get_storage_path(deploy_cfg, promote_from_env)
        log.info("Promote IG registry files {} -> {}".format(source_path, target_path))

    else:
        source_path = Path("./")
        log.info("Deploy IG registry files -> {}".format(target_path))

    confirm("Continue?", "Aborted by user", confirm_yes=confirm_yes, default=True)

    deploy_files = ["index.html", "package-feed.xml"]
    files = []
    for file in deploy_files:
        source_file = source_path / file
        target_file = target_path / file

        files.append((source_file, target_file))

        if dry_run:
            log.info("Would have copied {} -> {}".format(source_file, target_file))

        else:
            gcloud.copy(source=source_file, target=target_file, force=True)

    log.succ("Deployed IG registry files")
    return files


def deploy_ig(
    deploy_cfg: DeployConfig,
    target_env: str,
    promote_from_env: str | None = None,
    confirm_yes: bool = False,
    dry_run: bool = False,
    *args,
    **kwargs,
):

    if promote_from_env:
        # Get 'project' and 'version' from publication request
        project, version = project_version_from_pub_req()

        source_path = get_storage_path(deploy_cfg, promote_from_env) / project / version
        target_path = get_storage_path(deploy_cfg, target_env) / project / version

        log.info("Promote built IG {} -> {}".format(source_path, target_path))

    else:
        # Get 'project' and 'version' from built implementation guide
        project, version = project_version_from_imp_guide()

        source_path = Path("./output")
        target_path = get_storage_path(deploy_cfg, target_env) / project / version

        log.info("Deploy built IG -> {}".format(target_path))

    # Copy IG
    confirm("Continue?", "Aborted by user", confirm_yes=confirm_yes, default=True)

    if dry_run:
        log.info("Would have copied {} -> {}".format(source_path, target_path))

    else:
        gcloud.copy(source=source_path, target=target_path, force=confirm_yes)

    log.succ("Deployed IG")

    return source_path, target_path


def deploy_ig_meta(
    deploy_cfg: DeployConfig,
    target_env: str,
    promote_from_env: str | None = None,
    dry_run: bool = False,
    *args,
    **kwargs,
):

    if promote_from_env:
        # Get 'project' and 'version' from poblication request
        project, _ = project_version_from_pub_req()

        source_path = get_storage_path(deploy_cfg, promote_from_env) / project
        target_path = get_storage_path(deploy_cfg, target_env) / project

        log.info("Promote IG meta data {} -> {}".format(source_path, target_path))

    else:
        # Get 'project' and 'version' from built implementation guide
        project, _ = project_version_from_imp_guide()

        # Check possible source paths
        # First the current path
        if ((path := Path("./publish")) / "index.html").exists():
            source_path = path

        elif ((path := path / project) / "index.html").exists():
            source_path = path

        else:
            log.warn("Meta files not found, skipping")
            return []

        target_path = get_storage_path(deploy_cfg, target_env) / project

        log.info("Deploy IG meta data -> {}".format(target_path))

    # Copy meta files
    deploy_files = ["index.html", "package-list.json"]
    files = []
    for file in deploy_files:
        source_file = source_path / file
        target_file = target_path / file

        files.append((source_file, target_file))

        if dry_run:
            log.info("Would have copied {} -> {}".format(source_file, target_file))

        else:
            gcloud.copy(source=source_file, target=target_file, force=True)

    log.succ("Deployed IG meta files")
    return files


def get_storage_path(deploy_cfg: DeployConfig, env_name: str) -> Url:
    storage = deploy_cfg.env.get(env_name)

    if storage is None:
        raise Exception(f"Environment '{env_name}' not defined in config")

    storage = Url(storage) if storage.startswith("gs://") else Url("gs://" + storage)

    return storage / (deploy_cfg.path or TARGET_BASE_DIR)


def project_version_from_pub_req() -> tuple[str, str]:
    pub_req = Path(".") / "publication-request.json"

    if not pub_req.exists():
        raise Exception("Publication request missing")

    req = json.loads(pub_req.read_text(encoding="utf-8"))
    _, project, version = req["path"].rsplit("/", 2)

    return project, version


def project_version_from_imp_guide() -> tuple[str, str]:
    output_dir = Path("./output")
    igs = list(output_dir.glob("ImplementationGuide*.json"))
    if len(igs) != 1:
        raise Exception("Built IG not found")

    ig = json.loads(igs[0].read_text(encoding="utf-8"))
    return ig["url"].rsplit("/", 3)[1], ig["version"]


__doc__ = "Deploy IG"
__handler__ = deploy
__setup_parser__ = setup_parser
