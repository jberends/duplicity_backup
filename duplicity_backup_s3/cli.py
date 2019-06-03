# -*- coding: utf-8 -*-

"""Console script for duplicity_backup_s3."""
import sys

import click

from .defaults import CONTEXT_SETTINGS
from .commands.incr import incr
from .commands.init import init
from .commands.verify import verify


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


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
