import unittest
import subprocess


from commandnotfound import report


class CommandNotFoundPrintTest(unittest.TestCase):
    def test_simple(self):
        try:
            subprocess.run(["converT"])
        except FileNotFoundError as e:
            report(e)
