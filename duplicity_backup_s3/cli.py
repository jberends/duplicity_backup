# -*- coding: utf-8 -*-

"""Console script for duplicity_backup_s3."""
import sys

import click

from .commands.cleanup import cleanup
from .commands.incr import incr
from .commands.init import init
from .commands.list import list as list_files
from .commands.remove import remove
from .commands.status import status
from .commands.verify import verify
from .defaults import CONTEXT_SETTINGS


class AliasedGroup(click.Group):
    """Intermediate class to combine the duplicity_backup_s3 command groups."""

    pass


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option()
def main(**options):
    pass


main.add_command(incr)
main.add_command(verify)
# main.add_command(restore)
main.add_command(init)
main.add_command(cleanup)
main.add_command(status)
main.add_command(list_files)
main.add_command(remove)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
