import unittest

from fhir_scripts import check


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
