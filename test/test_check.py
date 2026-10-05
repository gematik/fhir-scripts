import json
import tempfile
import unittest
from pathlib import Path

from pydantic import AnyUrl

from fhir_scripts import check
from fhir_scripts.models.fhir.publication_request import PublicationRequestStatus
from fhir_scripts.models.fhir.sushi_config import SushiConfigStatus


class TestCheckDefVersions(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def setupFiles(self, input: list[dict]):
        for e in input:
            with tempfile.NamedTemporaryFile(
                mode="w+t",
                dir=self.tmpdir.name,
                suffix=".json",
                delete=False,
                delete_on_close=False,
            ) as file:
                file.write(json.dumps(e))
                file.close()

    def test_multiple_versions(self):
        input = [
            {"version": "1.2.3", "date": "2020-01-01"},
            {"version": "1.2.4", "date": "2022-01-01"},
        ]
        wanted = 0, 0
        self.setupFiles(input)

        res = check._check_def_versions(Path(self.tmpdir.name))
        self.assertEqual(wanted, res)

    def test_same_version_same_date(self):
        input = [
            {"version": "1.2.3", "date": "2020-01-01"},
            {"version": "1.2.3", "date": "2020-01-01"},
        ]
        wanted = 0, 0
        self.setupFiles(input)

        res = check._check_def_versions(Path(self.tmpdir.name))
        self.assertEqual(wanted, res)

    def test_same_version_diff_date(self):
        input = [
            {"version": "1.2.3", "date": "2020-01-01"},
            {"version": "1.2.3", "date": "2022-01-01"},
        ]
        wanted = 1, 0
        self.setupFiles(input)

        res = check._check_def_versions(Path(self.tmpdir.name))
        self.assertEqual(wanted, res)


class TestCheckVersions(unittest.TestCase):

    def test_matching(self):
        pub_request_version = "1.2.3"
        pub_request_desc = "Example IG 1.2.3"
        pub_request_path = AnyUrl("http://example.org/ExampleIG/1.2.3")
        sushi_config_version = "1.2.3"
        package_json_version = "1.2.3"

        wanted = 0, 0

        res = check._check_versions(
            pub_request_version,
            pub_request_desc,
            pub_request_path,
            sushi_config_version,
            package_json_version,
        )
        self.assertEqual(wanted, res)

    def test_pub_not_matching(self):
        pub_request_version = "1.2.4"
        pub_request_path = AnyUrl("http://example.org/ExampleIG/1.2.3")
        pub_request_desc = "Example IG 1.2.3"
        sushi_config_version = "1.2.3"
        package_json_version = "1.2.3"

        wanted = 1, 0

        res = check._check_versions(
            pub_request_version,
            pub_request_desc,
            pub_request_path,
            sushi_config_version,
            package_json_version,
        )
        self.assertEqual(wanted, res)

    def test_pub_path_not_matching(self):
        pub_request_version = "1.2.4"
        pub_request_path = AnyUrl("http://example.org/ExampleIG/1.2.4")
        pub_request_desc = "Example IG 1.2.3"
        sushi_config_version = "1.2.3"
        package_json_version = "1.2.3"

        wanted = 2, 0

        res = check._check_versions(
            pub_request_version,
            pub_request_desc,
            pub_request_path,
            sushi_config_version,
            package_json_version,
        )
        self.assertEqual(wanted, res)

    def test_pub_desc_not_matching(self):
        pub_request_version = "1.2.4"
        pub_request_path = AnyUrl("http://example.org/ExampleIG/1.2.4")
        pub_request_desc = "Example IG 1.2.4"
        sushi_config_version = "1.2.3"
        package_json_version = "1.2.3"
        wanted = 3, 0

        res = check._check_versions(
            pub_request_version,
            pub_request_desc,
            pub_request_path,
            sushi_config_version,
            package_json_version,
        )
        self.assertEqual(wanted, res)

    def test_sushi_not_matching(self):
        pub_request_version = "1.2.3"
        pub_request_path = AnyUrl("http://example.org/ExampleIG/1.2.3")
        pub_request_desc = "Example IG 1.2.3"
        sushi_config_version = "1.2.4"
        package_json_version = "1.2.3"

        wanted = 3, 0

        res = check._check_versions(
            pub_request_version,
            pub_request_desc,
            pub_request_path,
            sushi_config_version,
            package_json_version,
        )
        self.assertEqual(wanted, res)

    def test_package_not_matching(self):
        pub_request_version = "1.2.3"
        pub_request_path = AnyUrl("http://example.org/ExampleIG/1.2.3")
        pub_request_desc = "Example IG 1.2.3"
        sushi_config_version = "1.2.3"
        package_json_version = "1.2.4"

        wanted = 1, 0

        res = check._check_versions(
            pub_request_version,
            pub_request_desc,
            pub_request_path,
            sushi_config_version,
            package_json_version,
        )
        self.assertEqual(wanted, res)


class TestCheckDeps(unittest.TestCase):

    def test_matching(self):
        sushi_config_deps = {"org.example.abc": "1.2.3"}
        package_json_deps = {"org.example.abc": "1.2.3"}
        wanted = 0, 0

        result = check._check_deps(sushi_config_deps, package_json_deps)
        self.assertEqual(wanted, result)

    def test_not_matching(self):
        sushi_config_deps = {"org.example.abc": "1.2.3"}
        package_json_deps = {"org.example.abc": "1.2.4"}
        wanted = 1, 0

        result = check._check_deps(sushi_config_deps, package_json_deps)
        self.assertEqual(wanted, result)

    def test_not_matching_multiple(self):
        sushi_config_deps = {"org.example.abc": "1.2.3", "org.example.def": "4.5.6"}
        package_json_deps = {"org.example.abc": "1.2.4", "org.example.def": "4.5.7"}
        wanted = 2, 0

        result = check._check_deps(sushi_config_deps, package_json_deps)
        self.assertEqual(wanted, result)

    def test_not_in_sushi(self):
        sushi_config_deps = {}
        package_json_deps = {"org.example.abc": "1.2.3"}
        wanted = 0, 1

        result = check._check_deps(sushi_config_deps, package_json_deps)
        self.assertEqual(wanted, result)

    def test_no_deps_in_sushi(self):
        sushi_config_deps = {}
        package_json_deps = {"org.example.abc": "1.2.3"}
        wanted = 0, 1

        result = check._check_deps(sushi_config_deps, package_json_deps)
        self.assertEqual(wanted, result)

    def test_not_in_package(self):
        sushi_config_deps = {"org.example.abc": "1.2.3"}
        package_json_deps = {}
        wanted = 0, 1

        result = check._check_deps(sushi_config_deps, package_json_deps)
        self.assertEqual(wanted, result)

    def test_no_deps_in_package(self):
        sushi_config_deps = {"org.example.abc": "1.2.3"}
        package_json_deps = {}
        wanted = 0, 1

        result = check._check_deps(sushi_config_deps, package_json_deps)
        self.assertEqual(wanted, result)


class TestCheckTransitiveDeps(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def setupFiles(self, input: dict[str, dict[str, str]]):
        for pkg, deps in input.items():
            file = Path(self.tmpdir.name) / pkg / "package/package.json"
            file.parent.mkdir(parents=True, exist_ok=True)
            name, version = pkg.split("#")
            content = {"version": version, "name": name, "dependencies": deps}
            file.write_text(json.dumps(content), "utf-8")

    def test_matching(self):
        sushi_config_deps = {"org.example.abc": "1.2.3", "org.example.def": "4.5.6"}
        input_pkgs = {
            "org.example.abc#1.2.3": {"org.example.def": "4.5.6"},
            "org.example.def#4.5.6": {},
        }

        wanted = 0, 0
        self.setupFiles(input_pkgs)

        res = check._check_transitive_deps(sushi_config_deps, Path(self.tmpdir.name))
        self.assertEqual(wanted, res)

    def test_different(self):
        sushi_config_deps = {"org.example.abc": "1.2.3", "org.example.def": "4.5.6"}
        input_pkgs = {
            "org.example.abc#1.2.3": {"org.example.def": "4.5.7"},
            "org.example.def#4.5.6": {},
            "org.example.def#4.5.7": {},
        }

        wanted = 0, 1
        self.setupFiles(input_pkgs)

        res = check._check_transitive_deps(sushi_config_deps, Path(self.tmpdir.name))
        self.assertEqual(wanted, res)

    def test_missing(self):
        sushi_config_deps = {"org.example.abc": "1.2.3", "org.example.def": "4.5.6"}
        input_pkgs = {
            "org.example.abc#1.2.3": {"org.example.def": "4.5.6"},
        }

        wanted = 0, 2
        self.setupFiles(input_pkgs)

        res = check._check_transitive_deps(sushi_config_deps, Path(self.tmpdir.name))
        self.assertEqual(wanted, res)


class TestCheckRelease(unittest.TestCase):

    def test_sushi_correct(self):
        pub_request_status = PublicationRequestStatus.release
        sushi_config_status = SushiConfigStatus.active
        sushi_config_release_label = "release"

        wanted = 0, 0

        result = check._check_release(
            pub_request_status, sushi_config_status, sushi_config_release_label
        )
        self.assertEqual(wanted, result)

    def test_sushi_pub_status_draft(self):
        pub_request_status = PublicationRequestStatus.draft
        sushi_config_status = SushiConfigStatus.active
        sushi_config_release_label = "release"

        wanted = 1, 0

        result = check._check_release(
            pub_request_status, sushi_config_status, sushi_config_release_label
        )
        self.assertEqual(wanted, result)

    def test_sushi_sushi_status_draft(self):
        pub_request_status = PublicationRequestStatus.release
        sushi_config_status = SushiConfigStatus.draft
        sushi_config_release_label = "release"

        wanted = 1, 0

        result = check._check_release(
            pub_request_status, sushi_config_status, sushi_config_release_label
        )
        self.assertEqual(wanted, result)

    def test_sushi_pub_label_draft(self):
        pub_request_status = PublicationRequestStatus.release
        sushi_config_status = SushiConfigStatus.active
        sushi_config_release_label = "draft"

        wanted = 1, 0

        result = check._check_release(
            pub_request_status, sushi_config_status, sushi_config_release_label
        )
        self.assertEqual(wanted, result)

    def test_sushi_everything_draft(self):
        pub_request_status = PublicationRequestStatus.draft
        sushi_config_status = SushiConfigStatus.draft
        sushi_config_release_label = "draft"

        wanted = 3, 0

        result = check._check_release(
            pub_request_status, sushi_config_status, sushi_config_release_label
        )
        self.assertEqual(wanted, result)


class TestCheckGetVersion(unittest.TestCase):

    def test_basic(self):
        input = "1.2.3"
        wanted = "1.2.3"

        result = check._get_version(input)
        self.assertEqual(wanted, result)

    def test_not_allowed(self):
        input = "1.2.3.4"

        self.assertIsNone(check._get_version(input))

    def test_in_value(self):
        input = "IG with version 1.2.3"
        wanted = "1.2.3"

        result = check._get_version(input)
        self.assertEqual(wanted, result)

    def test_complex_variant1(self):
        input = "1.2.3-rc"
        wanted = "1.2.3-rc"

        result = check._get_version(input)
        self.assertEqual(wanted, result)

    def test_complex_variant2(self):
        input = "1.2.3-alpha"
        wanted = "1.2.3-alpha"

        result = check._get_version(input)
        self.assertEqual(wanted, result)

    def test_complex_not_allowed(self):
        input = "1.2.3-alpha-1"

        result = check._get_version(input)
        self.assertIsNone(result)

    def test_complex_variant3(self):
        input = "1.2.3-alpha.1"
        wanted = "1.2.3-alpha.1"

        result = check._get_version(input)
        self.assertEqual(wanted, result)

    def test_complex_in_value(self):
        input = "IG with version 1.2.3"
        wanted = "1.2.3"

        result = check._get_version(input)
        self.assertEqual(wanted, result)
