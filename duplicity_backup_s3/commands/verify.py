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
@click.option("--file", "--dir", "file", help="File or directory to verify.")
@click.option(
    "--time",
    help="Time of the backup to check. eg. '8h', '7D', '1M', 'now', '2019-06-03'",
)
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
def verify(**options):
    """Verify backup."""
    check_config_file(options.get("config"), verbose=options.get("verbose"))

    dup = DuplicityS3(**options)
    dup.do_verify()
