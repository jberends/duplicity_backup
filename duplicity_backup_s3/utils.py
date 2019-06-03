import os
import sys
from contextlib import contextmanager
from pathlib import Path

import click
from cerberus import SchemaError
from cerberus.errors import ValidationError


def echo_success(text, nl=True):
    """
    Write to the console as a success (Cyan bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg="cyan", bold=True, nl=nl)


def echo_failure(text, nl=True):
    """
    Write to the console as a failure (Red bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg="red", bold=True, nl=nl)


def echo_warning(text, nl=True):
    """
    Write to the console as a warning (Yellow bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg="yellow", bold=True, nl=nl)


def echo_waiting(text, nl=True):
    """
    Write to the console as a waiting (Magenta bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg="magenta", bold=True, nl=nl)


def echo_info(text, nl=True):
    """
    Write to the console as a informational (bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, bold=True, nl=nl)


"""
aws:
  AWS_ACCESS_KEY_ID: foobar_aws_key_id
  AWS_SECRET_ACCESS_KEY: foobar_aws_access_key
backuproot: /home
excludes:
  - _TESTFILE_TO_EXCLUDE
includes:
  - Pictures
remote:
  bucket: ''
  path: '__test'
"""

string_type = dict(type="string")

config_file_schema = dict(
    aws=dict(
        type="dict",
        allow_unknown=False,
        schema=dict(AWS_ACCESS_KEY_ID=string_type, AWS_SECRET_ACCESS_KEY=string_type),
    ),
    backuproot=string_type,
    includes=dict(type="list", items=[string_type]),
    excludes=dict(type="list", items=[string_type]),
    remote=dict(
        type="dict",
        allow_unknown=False,
        schema=dict(bucket=string_type, path=string_type),
    ),
)


def check_config_file(config_file, exit=True, verbose=False):
    """Check and return the full absolute Path to the config file other wise exit or return False.

    :param config_file: filename and/or path to the config file
    :param exit: when exit is true, exit with return_code 2
    """
    config_path = Path(Path.cwd() / config_file)
    if not config_path.exists():
        echo_failure(
            "Config file does not exist in '{}', please provide or "
            "create an empty one using the command `init`.".format(config_file)
        )
        if exit:
            sys.exit(2)
        else:
            return False

    # performing validation
    from cerberus import Validator
    import yaml

    with config_path.open() as fd:
        # try:
        validator = Validator()
        validator.allow_unknown = False
        if not validator.validate(yaml.safe_load(fd), config_file_schema):
            echo_failure(
                "The configuration file cannot be read: \n{}".format(validator.errors)
            )
            if exit:
                sys.exit(2)

    if verbose:
        echo_info(
            "The configuration file is succesfully validated against the validation schema"
        )
    return config_path


@contextmanager
def temp_chdir(cwd=None):
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="duplicity_s3__") as tempwd:
        origin = cwd or os.getcwd()
        os.chdir(tempwd)

        try:
            yield tempwd if os.path.exists(tempwd) else ""
        finally:
            os.chdir(origin)
