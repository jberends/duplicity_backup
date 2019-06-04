import sys
from pathlib import Path

import click
import yaml

from duplicity_backup_s3.defaults import (
    EMPTY_CONFIGFILE,
    CONTEXT_SETTINGS,
    CONFIG_FILEPATH,
)
from duplicity_backup_s3.utils import echo_info, echo_failure, check_config_file


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-c",
    "--config",
    help="Config file location. Alternatively set the environment variable: `DUPLICITY_BACKUP_S3_CONFIG`.",
    envvar="DUPLICITY_BACKUP_S3_CONFIG",
    default=CONFIG_FILEPATH,
)
@click.option(
    "--dry-run", envvar="DRY_RUN", is_flag=True, help="Dry run", default=False
)
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
def init(**options):
    """Initialise an empty configuration file."""

    config = check_config_file(
        options.get("config"), exit=False, verbose=options.get("verbose")
    )
    if config.exists() and not click.confirm(
        "Do you want to override the current '{}'".format(options.get("config"))
    ):
        echo_info("Exiting without overwriting current config file")
        sys.exit(1)

    if config.exists():
        echo_info("Backing up old config file.")
        deprecated_config_filename = Path("{}.backup".format(config.name))
        config.replace(deprecated_config_filename)

    with config.open("w") as fd:
        echo_info("Initialising an empty config file in: '{}'".format(config))
        fd.write(yaml.dump(EMPTY_CONFIGFILE))
    if config.exists():
        sys.exit(0)
    else:
        echo_failure(
            "Config file does not exist in '{}', please provide.".format(
                options.get("config")
            )
        )
        sys.exit(2)
