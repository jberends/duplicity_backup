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
    "--time",
    help="Time of the backup to check. eg. '8h', '7D', '1M', 'now', '2019-06-03', "
         "'2020-12-08T21:40:00+01:00'",
)
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
def list(**options):
    """List of the current files in the backup."""
    check_config_file(options.get("config"), verbose=options.get("verbose"))

    dup = DuplicityS3(**options)
    dup.do_list_current_files()
