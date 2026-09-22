import unittest
from argparse import Namespace

from fhir_scripts import cli


class TestParseEnvAsArgs(unittest.TestCase):

    def test_parse(self):

        input = {"OUTPUT_COLOR": "default"}

        res = cli.parse_env_as_args(input)

        self.assertTrue(hasattr(res, "output_color"))
        self.assertEqual(res.output_color, "default")


class TestMergeNamespaces(unittest.TestCase):

    def test_combine(self):
        args = {"foo": "bar"}
        env = {"foo_bar": "bar_foo"}

        wanted = {"foo": "bar", "foo_bar": "bar_foo"}

        res = cli.merge_namespaces(Namespace(**env), Namespace(**args))
        self.assertDictEqual(wanted, vars(res))

    def test_only_env(self):
        args = {}
        env = {"foo": "foobar"}

        wanted = {"foo": "foobar"}

        res = cli.merge_namespaces(Namespace(**env), Namespace(**args))
        self.assertDictEqual(wanted, vars(res))

    def test_overwrite(self):
        args = {"foo": "bar"}
        env = {"foo": "foobar"}

        wanted = {"foo": "bar"}

        res = cli.merge_namespaces(Namespace(**env), Namespace(**args))
        self.assertDictEqual(wanted, vars(res))
