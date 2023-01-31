import click

from duplicity_backup_s3 import __version__
from duplicity_backup_s3.commands.cleanup import cleanup
from duplicity_backup_s3.commands.incr import incr
from duplicity_backup_s3.commands.init import init
from duplicity_backup_s3.commands.list import list as list_files
from duplicity_backup_s3.commands.remove import remove
from duplicity_backup_s3.commands.restore import restore
from duplicity_backup_s3.commands.status import status
from duplicity_backup_s3.commands.verify import verify
from duplicity_backup_s3.defaults import CONTEXT_SETTINGS


class AliasedGroup(click.Group):
    """Intermediate class to combine the duplicity_backup_s3 command groups."""

    pass


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def duplicity_backup_s3():
    """Duplicity Backup to S3 wrapper."""
    pass


duplicity_backup_s3.add_command(incr)
duplicity_backup_s3.add_command(verify)
duplicity_backup_s3.add_command(restore)
duplicity_backup_s3.add_command(init)
duplicity_backup_s3.add_command(cleanup)
duplicity_backup_s3.add_command(status)
duplicity_backup_s3.add_command(list_files)
duplicity_backup_s3.add_command(remove)
