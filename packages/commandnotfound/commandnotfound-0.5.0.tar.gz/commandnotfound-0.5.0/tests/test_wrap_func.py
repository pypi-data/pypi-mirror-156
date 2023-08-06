import unittest
import subprocess


from commandnotfound import wrap


class CommandNotFoundWrapTest(unittest.TestCase):
    def test_simple(self):
        wrapped_run = wrap(subprocess.run)
        with self.assertRaises(FileNotFoundError):
            wrapped_run(["converT"])

    def test_wrap_check_output(self):
        wrapped_check_output = wrap(subprocess.check_output)
        out = wrapped_check_output("ls")
        self.assertTrue(out)
