import json
import tempfile
import unittest
from pathlib import Path

from fhir_scripts import check


class TestCheckDefVersions(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        return super().setUp()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        return super().tearDown()

    def setupFiles(self, input: list[dict]):
        for e in input:
            file = tempfile.NamedTemporaryFile(
                mode="w+t",
                dir=self.tmpdir.name,
                suffix=".json",
                delete=False,
                delete_on_close=False,
            )
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
        input_pub = {
            "version": "1.2.3",
            "path": "http://example.org/ExampleIG/1.2.3",
            "desc": "Example IG 1.2.3",
        }
        input_sushi = {"version": "1.2.3"}
        input_package = {"version": "1.2.3"}
        wanted = 0, 0

        res = check._check_versions(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, res)

    def test_pub_not_matching(self):
        input_pub = {
            "version": "1.2.4",
            "path": "http://example.org/ExampleIG/1.2.3",
            "desc": "Example IG 1.2.3",
        }
        input_sushi = {"version": "1.2.3"}
        input_package = {"version": "1.2.3"}
        wanted = 1, 0

        res = check._check_versions(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, res)

    def test_pub_path_not_matching(self):
        input_pub = {
            "version": "1.2.4",
            "path": "http://example.org/ExampleIG/1.2.4",
            "desc": "Example IG 1.2.3",
        }
        input_sushi = {"version": "1.2.3"}
        input_package = {"version": "1.2.3"}
        wanted = 2, 0

        res = check._check_versions(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, res)

    def test_pub_desc_not_matching(self):
        input_pub = {
            "version": "1.2.4",
            "path": "http://example.org/ExampleIG/1.2.4",
            "desc": "Example IG 1.2.4",
        }
        input_sushi = {"version": "1.2.3"}
        input_package = {"version": "1.2.3"}
        wanted = 3, 0

        res = check._check_versions(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, res)

    def test_sushi_not_matching(self):
        input_pub = {
            "version": "1.2.3",
            "path": "http://example.org/ExampleIG/1.2.3",
            "desc": "Example IG 1.2.3",
        }
        input_sushi = {"version": "1.2.4"}
        input_package = {"version": "1.2.3"}
        wanted = 3, 0

        res = check._check_versions(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, res)

    def test_package_not_matching(self):
        input_pub = {
            "version": "1.2.3",
            "path": "http://example.org/ExampleIG/1.2.3",
            "desc": "Example IG 1.2.3",
        }
        input_sushi = {"version": "1.2.3"}
        input_package = {"version": "1.2.4"}
        wanted = 1, 0

        res = check._check_versions(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, res)

    def test_version_missing(self):
        input_pub = {
            "version": "1.2.3",
            "path": "http://example.org/ExampleIG/1.2.3",
            "desc": "Example IG 1.2.3",
        }
        input_sushi = {"version": "1.2.3"}
        input_package = {}
        wanted = 1, 0

        res = check._check_versions(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, res)


class TestCheckDeps(unittest.TestCase):

    def test_matching(self):
        input_pub = {}
        input_sushi = {"dependencies": {"org.example.abc": "1.2.3"}}
        input_package = {"dependencies": {"org.example.abc": "1.2.3"}}
        wanted = 0, 0

        result = check._check_deps(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, result)

    def test_not_matching(self):
        input_pub = {}
        input_sushi = {"dependencies": {"org.example.abc": "1.2.3"}}
        input_package = {"dependencies": {"org.example.abc": "1.2.4"}}
        wanted = 1, 0

        result = check._check_deps(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, result)

    def test_not_matching_multiple(self):
        input_pub = {}
        input_sushi = {
            "dependencies": {"org.example.abc": "1.2.3", "org.example.def": "4.5.6"}
        }
        input_package = {
            "dependencies": {"org.example.abc": "1.2.4", "org.example.def": "4.5.7"}
        }
        wanted = 2, 0

        result = check._check_deps(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, result)

    def test_not_in_sushi(self):
        input_pub = {}
        input_sushi = {"dependencies": {}}
        input_package = {"dependencies": {"org.example.abc": "1.2.3"}}
        wanted = 0, 1

        result = check._check_deps(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, result)

    def test_no_deps_in_sushi(self):
        input_pub = {}
        input_sushi = {}
        input_package = {"dependencies": {"org.example.abc": "1.2.3"}}
        wanted = 0, 1

        result = check._check_deps(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, result)

    def test_not_in_package(self):
        input_pub = {}
        input_sushi = {"dependencies": {"org.example.abc": "1.2.3"}}
        input_package = {"dependencies": {}}
        wanted = 0, 1

        result = check._check_deps(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, result)

    def test_no_deps_in_package(self):
        input_pub = {}
        input_sushi = {"dependencies": {"org.example.abc": "1.2.3"}}
        input_package = {}
        wanted = 0, 1

        result = check._check_deps(input_pub, input_sushi, input_package)
        self.assertEqual(wanted, result)


class TestCheckRelease(unittest.TestCase):

    def test_sushi_correct(self):
        pub_request = {"status": "release"}
        sushi_config = {"status": "active", "releaseLabel": "release"}
        package_json = {}
        wanted = 0, 0

        result = check._check_release(pub_request, sushi_config, package_json)
        self.assertEqual(wanted, result)

    def test_sushi_pub_status_draft(self):
        pub_request = {"status": "draft"}
        sushi_config = {"status": "active", "releaseLabel": "release"}
        package_json = {}
        wanted = 1, 0

        result = check._check_release(pub_request, sushi_config, package_json)
        self.assertEqual(wanted, result)

    def test_sushi_sushi_status_draft(self):
        pub_request = {"status": "release"}
        sushi_config = {"status": "draft", "releaseLabel": "release"}
        package_json = {}
        wanted = 1, 0

        result = check._check_release(pub_request, sushi_config, package_json)
        self.assertEqual(wanted, result)

    def test_sushi_pub_label_draft(self):
        pub_request = {"status": "release"}
        sushi_config = {"status": "active", "releaseLabel": "draft"}
        package_json = {}
        wanted = 1, 0

        result = check._check_release(pub_request, sushi_config, package_json)
        self.assertEqual(wanted, result)

    def test_sushi_everything_draft(self):
        pub_request = {"status": "draft"}
        sushi_config = {"status": "draft", "releaseLabel": "draft"}
        package_json = {}
        wanted = 3, 0

        result = check._check_release(pub_request, sushi_config, package_json)
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

    def test_dict_without_key(self):
        input = {"version": "1.2.3"}

        result = check._get_version(input)
        self.assertIsNone(result)

    def test_dict_with_key(self):
        input = {"version": "1.2.3"}
        wanted = "1.2.3"

        result = check._get_version(input, "version")
        self.assertEqual(wanted, result)
