# -*- coding: utf-8 -*-

"""Console script for duplicity_backup_s3."""
import sys
from pathlib import Path
from pprint import pprint

import click
import yaml

from . import __version__
from .defaults import CONFIG_FILEPATH, EMPTY_CONFIGFILE
from .duplicity_s3 import DuplicityS3
from .utils import echo_failure, echo_info

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 88}
UNKNOWN_OPTIONS = {"ignore_unknown_options": True}.update(CONTEXT_SETTINGS)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option(
    "-c",
    "--config",
    help="Config file location",
    envvar="DUPLICITY_BACKUP_S3_CONFIG",
    default=CONFIG_FILEPATH,
)
@click.option(
    "--init", is_flag=True, help="Initialise a empty configuration YAML", default=False
)
@click.option(
    "--dry-run", envvar="DRY_RUN", is_flag=True, help="Dry run", default=False
)
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
def main(**options):
    """Console script for duplicity_backup_s3."""

    if options.get("init"):
        # do initialisation
        config = Path(Path.cwd() / options.get("config"))
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

    if options.get("config") is not None:
        config = Path(Path.cwd() / options.get("config"))
        if not config.exists():
            echo_failure(
                "Config file does not exist in '{}', please provide or "
                "create an empty one using `--init`.".format(options.get("config"))
            )
            sys.exit(2)

    dupe = DuplicityS3(**options)
    return dupe.do_incremental()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
