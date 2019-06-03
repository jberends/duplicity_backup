# -*- coding: utf-8 -*-

"""Console script for duplicity_backup_s3."""
import sys
from pprint import pprint

import click


@click.command()
@click.option("-c", "--config", help="Config file location")
def main(**options):
    """Console script for duplicity_backup_s3."""
    pprint(options)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
