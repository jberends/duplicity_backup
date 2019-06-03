#!/bin/env python
import sys

from .cli import duplicity_backup_s3

sys.exit(duplicity_backup_s3())
