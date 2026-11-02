import json
import unittest
from pathlib import Path
from unittest.mock import patch

from fhir_scripts import deploy
from fhir_scripts.models import config
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
        releaselabel = "release"
        wanted = (
            Path("output"),
            Url(f"gs://dev_bucket/ig/fhir/{project}/{version}"),
        )

        def read_text(*args, **kwargs):
            return json.dumps(
                {
                    "version": version,
                    "url": f"http://example.com/{project}/ImplementationGuide/com.example",
                    "definition": {
                        "extension": [
                            {
                                "extension": [
                                    {"url": "code", "valueString": "releaselabel"},
                                    {"url": "value", "valueString": releaselabel},
                                ],
                                "url": "http://hl7.org/fhir/tools/StructureDefinition/ig-parameter",
                            }
                        ]
                    },
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
            Url(f"gs://dev_bucket/ig/fhir/{project}/{version}"),
            Url(f"gs://prod_bucket/ig/fhir/{project}/{version}"),
        )

        def read_text(*args, **kwargs):
            return json.dumps({"path": f"http://example.com/{project}/{version}"})

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


class TestDeployIgCiBuild(unittest.TestCase):

    @patch(
        "fhir_scripts.deploy.Path.glob",
        lambda *args, **kwargs: [Path("ImplementationGuide.json")],
    )
    def test_local(self):
        cfg = config.DeployConfig(env={"dev": "dev_bucket"})
        project = "test_project"
        version = "1.2.3"
        releaselabel = "ci-build"
        wanted_main = (
            Path("output"),
            Url(f"gs://dev_bucket/ig/fhir/build/{project}"),
        )
        wanted_with_git_branch = (
            Path("output"),
            Url(f"gs://dev_bucket/ig/fhir/build/{project}/branches/BRANCH"),
        )

        def read_text(*args, **kwargs):
            return json.dumps(
                {
                    "version": version,
                    "url": f"http://example.com/{project}/ImplementationGuide/com.example",
                    "definition": {
                        "extension": [
                            {
                                "extension": [
                                    {"url": "code", "valueString": "releaselabel"},
                                    {"url": "value", "valueString": releaselabel},
                                ],
                                "url": "http://hl7.org/fhir/tools/StructureDefinition/ig-parameter",
                            }
                        ]
                    },
                }
            )

        with (
            patch("fhir_scripts.deploy.Path.read_text", side_effect=read_text),
            patch("fhir_scripts.deploy.subprocess.check_output", return_value="main"),
        ):
            res = deploy.deploy_ig(
                cfg, "dev", ig_output=Path("output"), dry_run=True, confirm_yes=True
            )
        self.assertEqual(wanted_main, res)

        with (
            patch("fhir_scripts.deploy.Path.read_text", side_effect=read_text),
            patch("fhir_scripts.deploy.subprocess.check_output", return_value="BRANCH"),
        ):
            res = deploy.deploy_ig(
                cfg, "dev", ig_output=Path("output"), dry_run=True, confirm_yes=True
            )
        self.assertEqual(wanted_with_git_branch, res)


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
                Url(f"gs://dev_bucket/ig/fhir/{project}/index.html"),
            ),
            (
                Path("publish/package-list.json"),
                Url(f"gs://dev_bucket/ig/fhir/{project}/package-list.json"),
            ),
        ]

        def read_text(*args, **kwargs):
            return json.dumps(
                {
                    "version": version,
                    "url": f"http://example.com/{project}/ImplementationGuide/com.example",
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
                Url(f"gs://dev_bucket/ig/fhir/{project}/index.html"),
                Url(f"gs://prod_bucket/ig/fhir/{project}/index.html"),
            ),
            (
                Url(f"gs://dev_bucket/ig/fhir/{project}/package-list.json"),
                Url(f"gs://prod_bucket/ig/fhir/{project}/package-list.json"),
            ),
        ]

        def read_text(*args, **kwargs):
            return json.dumps({"path": f"http://example.com/{project}/{version}"})

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
