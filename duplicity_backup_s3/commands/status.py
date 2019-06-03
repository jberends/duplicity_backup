import click

from duplicity_backup_s3.defaults import CONTEXT_SETTINGS, CONFIG_FILEPATH
from duplicity_backup_s3.duplicity_s3 import DuplicityS3
from duplicity_backup_s3.utils import check_config_file


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-c",
    "--config",
    help="Config file location. Alternatively set the environment variable: `DUPLICITY_BACKUP_S3_CONFIG`.",
    envvar="DUPLICITY_BACKUP_S3_CONFIG",
    default=CONFIG_FILEPATH,
)
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
def status(**options):
    """Status of the backup collection."""
    check_config_file(options.get("config"), verbose=options.get("verbose"))

    dup = DuplicityS3(**options)
    dup.do_collection_status()
