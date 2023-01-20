from pathlib import Path

import click

from duplicity_backup_s3.config import check_config_file
from duplicity_backup_s3.defaults import CONFIG_FILEPATH, CONTEXT_SETTINGS
from duplicity_backup_s3.duplicity_s3 import DuplicityS3


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-c",
    "--config",
    help="Config file location. Alternatively set the environment variable: "
         "`DUPLICITY_BACKUP_S3_CONFIG`.",
    envvar="DUPLICITY_BACKUP_S3_CONFIG",
    default=CONFIG_FILEPATH,
)
@click.option(
    "--dry-run", envvar="DRY_RUN", is_flag=True, help="Dry run", default=False
)
@click.option(
    "--file", "--dir", "file", help="File or directory to restore from the backup."
)
@click.option(
    "--time",
    help="Time of the backup to restore from. eg. '8h', '7D', '1M', 'now', '2019-06-03', '2020-12-08T21:40:00+01:00'",
)
@click.option(
    "--target",
    "target",
    help="Target directory where to restore the files to (is a dir and writable) [default={}]".format(
        Path.cwd()
    ),
    type=click.Path(dir_okay=True, writable=True),
    default=Path.cwd(),
)
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
@click.option("--debug", is_flag=True, help="Be even more verbose", default=False)
def restore(**options):
    """Perform a Restore of a backup."""
    check_config_file(options.get("config"), verbose=options.get("verbose"))

    dupe = DuplicityS3(**options)
    return dupe.do_restore()
