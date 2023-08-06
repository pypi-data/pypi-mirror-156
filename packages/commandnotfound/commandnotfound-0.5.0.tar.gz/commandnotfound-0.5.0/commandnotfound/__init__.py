from typing import Union
import os
import subprocess


command_not_found_command_list = [
    "/usr/lib/command-not-found",  # apt-based distribution
    "/usr/libexec/pk-command-not-found",  # yum-based distribution
]


class CommandNotFoundValueError(ValueError):
    pass


def _report(e: Union[FileNotFoundError, str]) -> None:
    """For a given command name or instance of FileNotFoundError, execute the command-not-found command to display the error message.
    """
    for cnfc in command_not_found_command_list:
        if os.path.exists(cnfc):
            if isinstance(e, FileNotFoundError):
                command_name = e.filename
            elif isinstance(e, str):
                command_name = e
            else:
                raise CommandNotFoundValueError(e)
            _ret_code = subprocess.call([cnfc, command_name])


report = _report


def wrap(func):
    """Wrap subprocess.run function to call command-not-found commands as needed.
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            _report(e)
            raise e
    return inner
