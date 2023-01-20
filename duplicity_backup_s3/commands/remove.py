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
@click.option("--file", "--dir", "file", help="File or directory to verify.")
@click.option(
    "--older-than",
    "time",
    help="Delete all backup sets older than given time. eg. '8h', '7D', '1M', 'now', "
         "'2019-06-03', '2020-12-08T21:40:00+01:00'. Old backup sets will not be deleted "
         "if backup sets newer than time depend on them. Use `--force` to actually "
         "delete them.",
)
@click.option(
    "--all-but-n-full",
    type=int,
    help="Delete all backups sets that are older than the <COUNT> last full backup "
         "(in other words, keep the last count full backups and associated "
         "incremental sets). <COUNT> must be larger than zero. A value of 1 means "
         "that only the single most recent backup chain will be kept. Note that "
         "--force will be needed to delete the files instead of just listing them.",
)
@click.option(
    "--all-incremental-but-n-full",
    "--all-inc-but-n-full",
    type=int,
    help="Delete *incremental* sets of all backups sets that are older than the "
         "<COUNT> last full backup (in other words, keep only old full backups and "
         "not their increments). <COUNT> must be larger than zero. A value of 1 "
         "means that only the single most recent backup chain will be kept intact. "
         "Note that --force will be needed to delete the files instead of just "
         "listing them.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Actually delete the files on the remote instead of only listing them.",
    default=False,
)
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
def remove(**options):
    """Remove older backups."""
    check_config_file(options.get("config"), verbose=options.get("verbose"))

    dup = DuplicityS3(**options)
    dup.do_remove_older()
