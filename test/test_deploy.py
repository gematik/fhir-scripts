import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts import deploy
from fhir_scripts.models import config
from fhir_scripts.multiig import working_directory
from fhir_scripts.types import Url


class TestDeployIgRegistry(unittest.TestCase):

    def test_local(self):
        cfg = config.DeployConfig(env={"dev": "dev_bucket"})
        wanted = [
            (Path("index.html"), Url("gs://dev_bucket/ig/fhir/index.html")),
            (Path("package-feed.xml"), Url("gs://dev_bucket/ig/fhir/package-feed.xml")),
        ]

        res = deploy.deploy_ig_registry(cfg, "dev", dry_run=True, confirm_yes=True)
        self.assertListEqual(wanted, res)

    def test_promote(self):
        cfg = config.DeployConfig(env={"dev": "dev_bucket", "prod": "prod_bucket"})
        wanted = [
            (
                Url("gs://dev_bucket/ig/fhir/index.html"),
                Url("gs://prod_bucket/ig/fhir/index.html"),
            ),
            (
                Url("gs://dev_bucket/ig/fhir/package-feed.xml"),
                Url("gs://prod_bucket/ig/fhir/package-feed.xml"),
            ),
        ]

        res = deploy.deploy_ig_registry(
            cfg, "prod", promote_from_env="dev", dry_run=True, confirm_yes=True
        )
        self.assertListEqual(wanted, res)


class TestDeployIg(unittest.TestCase):

    @patch(
        "fhir_scripts.deploy.Path.glob",
        lambda *args, **kwargs: [Path("ImplementationGuide.json")],
    )
    def test_local(self):
        cfg = config.DeployConfig(env={"dev": "dev_bucket"})
        project = "test_project"
        version = "1.2.3"
        wanted = (
            Path("output"),
            Url("gs://dev_bucket/ig/fhir/{}/{}".format(project, version)),
        )

        def read_text(*args, **kwargs):
            return json.dumps(
                {
                    "version": version,
                    "url": "http://example.com/{}/ImplementationGuide/com.example".format(
                        project
                    ),
                }
            )

        with patch("fhir_scripts.deploy.Path.read_text", side_effect=read_text):
            res = deploy.deploy_ig(
                cfg, "dev", ig_output=Path("output"), dry_run=True, confirm_yes=True
            )

        self.assertEqual(wanted, res)

    @patch("fhir_scripts.deploy.Path.exists", lambda *args, **kwargs: True)
    def test_promote(self):
        cfg = config.DeployConfig(env={"dev": "dev_bucket", "prod": "prod_bucket"})
        project = "test_project"
        version = "1.2.3"
        wanted = (
            Url("gs://dev_bucket/ig/fhir/{}/{}".format(project, version)),
            Url("gs://prod_bucket/ig/fhir/{}/{}".format(project, version)),
        )

        def read_text(*args, **kwargs):
            return json.dumps(
                {"path": "http://example.com/{}/{}".format(project, version)}
            )

        with patch("fhir_scripts.deploy.Path.read_text", side_effect=read_text):
            res = deploy.deploy_ig(
                cfg,
                "prod",
                ig_output=Path("output"),
                promote_from_env="dev",
                dry_run=True,
                confirm_yes=True,
            )

        self.assertEqual(wanted, res)


class TestDeployIgMeta(unittest.TestCase):

    @patch(
        "fhir_scripts.deploy.Path.glob",
        lambda *args, **kwargs: [Path("ImplementationGuide.json")],
    )
    @patch("fhir_scripts.deploy.Path.exists", lambda *args, **kwargs: True)
    def test_local(self):
        cfg = config.DeployConfig(env={"dev": "dev_bucket"})
        project = "test_project"
        version = "1.2.3"
        wanted = [
            (
                Path("publish/index.html"),
                Url("gs://dev_bucket/ig/fhir/{}/index.html".format(project)),
            ),
            (
                Path("publish/package-list.json"),
                Url("gs://dev_bucket/ig/fhir/{}/package-list.json".format(project)),
            ),
        ]

        def read_text(*args, **kwargs):
            return json.dumps(
                {
                    "version": version,
                    "url": "http://example.com/{}/ImplementationGuide/com.example".format(
                        project
                    ),
                }
            )

        with patch("fhir_scripts.deploy.Path.read_text", side_effect=read_text):
            res = deploy.deploy_ig_meta(
                cfg, "dev", ig_output=Path("output"), dry_run=True, confirm_yes=True
            )

        self.assertListEqual(wanted, res)

    @patch("fhir_scripts.deploy.Path.exists", lambda *args, **kwargs: True)
    def test_promote(self):
        cfg = config.DeployConfig(env={"dev": "dev_bucket", "prod": "prod_bucket"})
        project = "test_project"
        version = "1.2.3"
        wanted = [
            (
                Url("gs://dev_bucket/ig/fhir/{}/index.html".format(project)),
                Url("gs://prod_bucket/ig/fhir/{}/index.html".format(project)),
            ),
            (
                Url("gs://dev_bucket/ig/fhir/{}/package-list.json".format(project)),
                Url("gs://prod_bucket/ig/fhir/{}/package-list.json".format(project)),
            ),
        ]

        def read_text(*args, **kwargs):
            return json.dumps(
                {"path": "http://example.com/{}/{}".format(project, version)}
            )

        with patch("fhir_scripts.deploy.Path.read_text", side_effect=read_text):
            res = deploy.deploy_ig_meta(
                cfg,
                "prod",
                ig_output=Path("output"),
                promote_from_env="dev",
                dry_run=True,
                confirm_yes=True,
            )

        self.assertEqual(wanted, res)


class TestDeployMultiIg(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmpdir.name)

        (self.repo / "fhirscripts.multiig.config.yaml").write_text(
            "version: 1\nigsRoot: igs\n",
            "utf-8",
        )

        for name in ["core", "rx"]:
            ig_dir = self.repo / "igs" / name
            ig_dir.mkdir(parents=True, exist_ok=True)
            (ig_dir / "fhirscripts.config.yaml").write_text(
                "deploy:\n  env:\n    dev: dev_bucket\n",
                "utf-8",
            )

        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def test_deploy_all_uses_ig_local_config(self):
        calls = []

        def deploy_ig_stub(*args, **kwargs):
            calls.append(Path.cwd().name)

        with patch("fhir_scripts.deploy.deploy_ig", side_effect=deploy_ig_stub):
            with patch("fhir_scripts.deploy.deploy_ig_meta", lambda *a, **k: None):
                with working_directory(self.repo):
                    deploy.deploy(
                        config=config.Config(),
                        environment="dev",
                        ig_output=Path("output"),
                        ig=[],
                        all=True,
                        dry_run=True,
                        yes=True,
                    )

        self.assertEqual(["core", "rx"], calls)
