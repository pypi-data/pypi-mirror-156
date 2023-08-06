import unittest
import subprocess


from commandnotfound import report, CommandNotFoundValueError


class CommandNotFoundPrintTest(unittest.TestCase):
    def test_simple(self):
        try:
            subprocess.run(["converT"])
        except FileNotFoundError as e:
            report(e)

    def test_for_str_value(self):
        report("converT")

    def test_for_invalid_value(self):
        with self.assertRaises(CommandNotFoundValueError):
            report(1)

