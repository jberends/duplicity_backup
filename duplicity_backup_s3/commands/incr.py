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
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
@click.option("--debug", is_flag=True, help="Be even more verbose", default=False)
def incr(**options):
    """Perform an Incremental backup."""
    check_config_file(options.get("config"), verbose=options.get("verbose"))

    dupe = DuplicityS3(**options)
    return dupe.do_incremental()
