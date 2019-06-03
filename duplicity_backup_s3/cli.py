# -*- coding: utf-8 -*-

"""Console script for duplicity_backup_s3."""
import sys
from pathlib import Path
from pprint import pprint

import click

from . import __version__
from .defaults import CONFIG_FILEPATH
from .duplicity_s3 import DuplicityS3
from .utils import echo_failure

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 110}
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
@click.option("--dry-run", is_flag=True, help="Dry run", default=False)
def main(**options):
    """Console script for duplicity_backup_s3."""

    if options.get('config') is not None:
        config = Path(options.get('config'))
        if not config.exists():
            echo_failure(
                "Config file does not exist in '{}', please provide.".format(
                    options.get("config")
                )
            )
            sys.exit(2)

    dup = DuplicityS3(**options)
    dup.do_incremental()

    return 0

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
