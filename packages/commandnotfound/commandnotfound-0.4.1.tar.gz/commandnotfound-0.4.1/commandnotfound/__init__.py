import os
import subprocess


command_not_found_command_list = [
    "/usr/lib/command-not-found",  # apt-based distribution
    "/usr/libexec/pk-command-not-found",  # yum-based distribution
]


def _report(e: FileNotFoundError) -> None:
    for cnfc in command_not_found_command_list:
        if os.path.exists(cnfc):
            command_name = e.filename
            _ret_code = subprocess.call([cnfc, command_name])


report = _report


def wrap(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            _report(e)
            raise e
    return inner
