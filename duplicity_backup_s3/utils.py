import os
from contextlib import contextmanager

import click


def echo_success(text: str, nl: bool = True) -> None:
    """
    Write to the console as a success (Cyan bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg="cyan", bold=True, nl=nl)


def echo_failure(text: str, nl: bool = True) -> None:
    """
    Write to the console as a failure (Red bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg="red", bold=True, nl=nl)


def echo_warning(text: str, nl: bool = True) -> None:
    """
    Write to the console as a warning (Yellow bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg="yellow", bold=True, nl=nl)


def echo_waiting(text: str, nl: bool = True) -> None:
    """
    Write to the console as a waiting (Magenta bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg="magenta", bold=True, nl=nl)


def echo_info(text: str, nl=True):
    """
    Write to the console as a informational (bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, bold=True, nl=nl)


@contextmanager
def temp_chdir(cwd=None):
    """Create temporary directory and change to it as a context to operate in.

    :param cwd: current working directory to change back to.
    """
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="duplicity_s3__") as tempwd:
        origin = cwd or os.getcwd()
        os.chdir(tempwd)

        try:
            yield tempwd if os.path.exists(tempwd) else ""
        finally:
            os.chdir(origin)


def run_as_root() -> bool:
    """When the user that runs the app is root, return True."""
    import os

    return os.geteuid() == 0
