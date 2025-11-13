import unittest
from unittest.mock import patch

from fhir_scripts.exception import CancelException
from fhir_scripts.helper import confirm


class TestHelperConfirm(unittest.TestCase):

    def test_force_yes(self):
        try:
            confirm("test", "test failed", confirm_yes=True)

        except CancelException:
            self.fail("Should not raise exception when forced")

    @patch("builtins.input", return_value="y")
    def test_input_y(self, mock_input):
        try:
            confirm("test", "test failed")

        except CancelException:
            self.fail("Should not raise exception when confirmed with 'y'")

    @patch("builtins.input", return_value="yes")
    def test_input_yes(self, mock_input):
        try:
            confirm("test", "test failed")

        except CancelException:
            self.fail("Should not raise exception when confirmed with 'yes'")

    @patch("builtins.input", return_value="n")
    def test_input_n(self, mock_input):
        try:
            confirm("test", "test failed")

        except CancelException:
            pass

        else:
            self.fail("Did not raise CancelException when input 'n'")

    @patch("builtins.input", return_value="no")
    def test_input_no(self, mock_input):
        try:
            confirm("test", "test failed")

        except CancelException:
            pass

        else:
            self.fail("Did not raise CancelException when input 'no'")

    @patch("builtins.input", return_value="")
    def test_default_yes(self, mock_input):
        try:
            confirm("test", "test failed", default=True)

        except CancelException:
            self.fail("Should not raise exception with default 'yes'")

    @patch("builtins.input", return_value="")
    def test_default_no(self, mock_input):
        try:
            confirm("test", "test failed")

        except CancelException:
            pass

        else:
            self.fail("Did not raise CancelException with default 'no'")
