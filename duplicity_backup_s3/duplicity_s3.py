# -*- coding: utf-8 -*-
import os
import subprocess
from pathlib import Path
from pprint import pprint
from typing import Dict

import yaml
from envparse import env

from duplicity_backup_s3.defaults import (
    FULL_IF_OLDER_THAN,
    DUPLICITY_BACKUP_ARGS,
    DUPLICITY_VERBOSITY,
    NEED_SUBPROCESS_SHELL,
    DUPLICITY_MORE_VERBOSITY,
    DUPLICITY_BASIC_ARGS,
    DUPLICITY_DEBUG_VERBOSITY)


# /bin/duplicity
#   -v3
#   --dry-run
#   --full-if-older-than 7D
#   --s3-use-new-style
#   --s3-european-buckets
#   --no-encryption
#   --exclude-device-files
#   --include=/opt/ke-chain/*-media
#   --include=/opt/ke-chain/var/archives
#   --exclude=**
#   /opt/ke-chain/   # src
#   s3+http://kew-prod-backup-target/kec-prod23/  # target

from duplicity_backup_s3.utils import echo_info


class DuplicityS3(object):
    def __init__(self, **options):
        self._config_file = Path(Path.cwd() / options.get("config"))
        self.options = options
        self.read_config(path=self._config_file)
        self.verbose = options.get("verbose", False)
        # in case of verbosity be more than 3 verbose
        duplicity_verbosity = (
            DUPLICITY_MORE_VERBOSITY if options.get("verbose") else DUPLICITY_VERBOSITY
        )
        if options.get('debug'):
            duplicity_verbosity = DUPLICITY_DEBUG_VERBOSITY

        self._args = ["-v{}".format(duplicity_verbosity)] + DUPLICITY_BASIC_ARGS

        self.dry_run = options.get("dry_run", False)

        # setting environment
        self.env = env
        self.env.read_envfile()

    def read_config(self, path: Path = None) -> None:
        """Read the config file.

        Stores the configuration in the protected variable `self._config`.
        """
        if path is None:
            path = self._config_file

        self._config = {}
        with self._config_file.open() as fd:
            self._config = yaml.safe_load(fd)

    def get_aws_secrets(self) -> Dict:
        """AWS secrets either from the environment or from the configuration file."""
        if (
            "aws" in self._config
            and "AWS_SECRET_ACCESS_KEY" in self._config.get("aws")
            and "AWS_ACCESS_KEY_ID" in self._config.get("aws")
        ):
            return self._config.get("aws")
        else:
            return dict(
                AWS_ACCESS_KEY_ID=self.env("AWS_ACCESS_KEY_ID", default="")
                or self._config.get("aws"),
                AWS_SECRET_ACCESS_KEY=self.env("AWS_SECRET_ACCESS_KEY", default=""),
            )

    def get_cludes(self, includes=None, excludes=None):
        """
        Get includes or excludes command arguments.

        :param includes: list of file includes (absolute paths, not relative from root)
        :param excludes: list of file exludes (absolute paths, not relative from root)
        :return:
        """
        arg_list = []
        if includes:
            arg_list.extend(["--include={}".format(path) for path in includes])
        if excludes:
            arg_list.extend(["--exclude={}".format(path) for path in excludes])
        return arg_list

    def do_incremental(self):
        """
        Incremental duplicity Backup.

        :return: error code
        """
        source = self._config.get("backuproot")
        target = "s3+http://{bucket}/{path}".format(**self._config.get("remote"))
        args = (
            self._args
            + DUPLICITY_BACKUP_ARGS
            + ["--full-if-older-than", str(FULL_IF_OLDER_THAN)]
            + self.get_cludes(
                includes=self._config.get("includes"),
                excludes=self._config.get("excludes"),
            )
        )
        runtime_env = self.get_aws_secrets()
        action = "inc"

        if self.dry_run:
            args.append("--dry-run")

        return self._execute(action, *args, source, target, runtime_env=runtime_env)

    def do_restore(self):
        raise NotImplementedError("Not yet, bro (https://youtu.be/rLwbzGyC6t4?t=52)")

    def do_verify(self):
        """Verify the backup.

        From the duplicity man page:
        Verify [--compare-data] [--time <time>] [--file-to-restore <rel_path>] <url> <local_path>
            Restore backup contents temporarily file by file and compare against the local path’s contents.
            duplicity will exit with a non-zero error level if any files are different. On verbosity level
            info (4) or higher, a message for each file that has changed will be logged.

            The --file-to-restore option restricts verify to that file or folder. The --time option allows to
            select a backup to verify against. The --compare-data option enables data comparison.

        :return: return_code of duplicity
        """

        from duplicity_backup_s3.utils import temp_chdir

        with temp_chdir() as target:
            source = "s3+http://{bucket}/{path}".format(**self._config.get("remote"))
            args = self._args
            runtime_env = self.get_aws_secrets()
            action = "verify"

            if self.dry_run:
                args.append("--dry-run")

            if self.options.get("file") is not None:
                args.extend(["--file-to-restore", self.options.get("file")])

            if self.verbose:
                echo_info("verifying backup in directory: {}".format(target))

            return self._execute(action, *args, source, target, runtime_env=runtime_env)

    def _execute(self, *cmd_args, runtime_env=None):
        """Execute the duplicity command."""

        command = [self._duplicity_cmd(), *cmd_args]

        self.last_results = subprocess.run(
            command, shell=NEED_SUBPROCESS_SHELL, env=runtime_env
        )

        if self.verbose:
            print("command used:")
            pprint([*cmd_args])
            print("environment:")
            pprint(
                [
                    "{} = {}".format(k, v)
                    for k, v in os.environ.items()
                    if ("SECRET" not in k) and (("AWS" in k) or ("DUPLICITY" in k))
                ]
            )

        return self.last_results.returncode

    def _duplicity_cmd(self, search_path=None):
        """
        Check if duplicity is installed and return version.

        :param search_path: path to search for duplicity if not in PATH. defaults None.
        :return:
        """
        from shutil import which

        duplicity_cmd = which("duplicity", path=search_path)

        if not duplicity_cmd:
            return OSError("Could not find `duplicity` in path, is it installed?")

        return duplicity_cmd


def duplicity_cmd(search_path=None):
    """
    Check if duplicity is installed and return version.

    :param search_path: path to search for duplicity if not in PATH. defaults None.
    :return:
    """
    from shutil import which

    duplicity_cmd = which("duplicity", path=search_path)

    if not duplicity_cmd:
        return OSError("Could not find `duplicity` in path, is it installed?")

    return duplicity_cmd
