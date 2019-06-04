# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import warnings
from pathlib import Path
from pprint import pprint
from typing import Dict, Optional, List

import yaml
from envparse import env

from duplicity_backup_s3.defaults import (
    FULL_IF_OLDER_THAN,
    DUPLICITY_BACKUP_ARGS,
    DUPLICITY_VERBOSITY,
    NEED_SUBPROCESS_SHELL,
    DUPLICITY_MORE_VERBOSITY,
    DUPLICITY_BASIC_ARGS,
    DUPLICITY_DEBUG_VERBOSITY,
)
from duplicity_backup_s3.utils import echo_info, echo_failure


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
        if options.get("debug"):
            duplicity_verbosity = DUPLICITY_DEBUG_VERBOSITY

        self._args = ["-v{}".format(duplicity_verbosity)] + DUPLICITY_BASIC_ARGS

        self.dry_run = options.get("dry_run", False)

        # setting environment
        self.env = env
        with warnings.catch_warnings():  # catch the warnings that env puts out.
            warnings.simplefilter("ignore", UserWarning)
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

    def _execute(self, *cmd_args, runtime_env: Dict = None) -> int:
        """Execute the duplicity command."""

        command = [self.duplicity_cmd(), *cmd_args]

        if self.verbose:
            print("command used:")
            print([*cmd_args])
            print("environment:")
            pprint(
                [
                    "{} = {}".format(k, v)
                    for k, v in os.environ.items()
                    if ("SECRET" not in k) and (("AWS" in k) or ("DUPLICITY" in k))
                ]
            )

        self.last_results = subprocess.run(
            command, shell=NEED_SUBPROCESS_SHELL, env=runtime_env
        )

        try:
            self.last_results.check_returncode()
        except subprocess.CalledProcessError as e:
            echo_failure(
                "The duplicity command exitted with an error. Command may not have succeeded."
            )
            if self.verbose:
                echo_info("More information on the error:\n{}".format(e.output))
        return self.last_results.returncode

    @classmethod
    def duplicity_cmd(cls, search_path=None) -> str:
        """
        Check if duplicity is installed and return version.

        :param search_path: path to search for duplicity if not in PATH. defaults None.
        :return: path to duplicity
        :raises OSError: When the duplicity command is not found in PATH.
        """
        from shutil import which

        duplicity_cmd = which("duplicity", path=search_path)

        if not duplicity_cmd:
            raise OSError("Could not find `duplicity` in path, is it installed?")

        return duplicity_cmd

    def get_cludes(
            self, includes: List[str] = None, excludes: List[str] = None
        ) -> List[str]:
        """
        Get includes or excludes command arguments.

        :param includes: list of file includes (absolute paths, not relative from root)
        :param excludes: list of file exludes (absolute paths, not relative from root)
        :return:
        """
        arg_list = []
        if includes:
            arg_list.extend([
                "--include={}".format(path) for path in includes
            ])
        if excludes:
            arg_list.extend(["--exclude={}".format(path) for path in excludes])
        return arg_list

    def do_incremental(self) -> int:
        """
        Incremental duplicity Backup.

        :return: error code
        """
        source = self._config.get("backuproot")
        target = "s3+http://{bucket}/{path}".format(**self._config.get("remote"))
        args = (
            self._args
            + DUPLICITY_BACKUP_ARGS
            + [
                "--full-if-older-than",
                self._config.get("full_if_older_than", FULL_IF_OLDER_THAN),
            ]
            + self.get_cludes(
                includes=self._config.get("includes"),
                excludes=self._config.get("excludes"),
            )
        )
        runtime_env = self.get_aws_secrets()
        action = "incr"

        if self.dry_run:
            args.append("--dry-run")

        return self._execute(action, *args, source, target, runtime_env=runtime_env)

    def do_restore(self) -> int:
        raise NotImplementedError("Not yet, bro (https://youtu.be/rLwbzGyC6t4?t=52)")

    def do_verify(self) -> int:
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

            if self.options.get("time") is not None:
                args.extend(["--time", self.options.get("time")])

            if self.verbose:
                echo_info("verifying backup in directory: {}".format(target))

            return self._execute(action, *args, source, target, runtime_env=runtime_env)

    def do_cleanup(self) -> int:
        """
        Cleanup of dirty remote.

        From the duplicity manpage:
        cleanup [--force] [--extra-clean] <url>
            Delete the extraneous duplicity files on the given backend. Non-duplicity files, or files in complete
            data sets will not be deleted. This should only be necessary after a duplicity session fails or is
            aborted prematurely. Note that --force will be needed to delete the files instead of just listing them.

        :return: returncode
        """
        target = "s3+http://{bucket}/{path}".format(**self._config.get("remote"))
        args = self._args
        runtime_env = self.get_aws_secrets()
        action = "cleanup"

        if self.dry_run:
            args.append("--dry-run")

        if self.options.get("force"):
            args.append("--force")

        if self.verbose:
            echo_info("Cleanup the backup in target: '{}'".format(target))

        return self._execute(action, *args, target, runtime_env=runtime_env)

    def do_collection_status(self) -> int:
        """
        Collection status of the backup.

        From the docs:
        collection-status <url>
            Summarize the status of the backup repository by printing the chains and sets found, and the
            number of volumes in each.

        :return: returncode
        """
        target = "s3+http://{bucket}/{path}".format(**self._config.get("remote"))
        action = "collection-status"

        if self.verbose:
            echo_info("Collection status of the backup in target: '{}'".format(target))

        return self._execute(
            action, *self._args, target, runtime_env=self.get_aws_secrets()
        )

    def do_list_current_files(self) -> int:
        """
        List current files included in the backup.

        from the docs:
        list-current-files [--time <time>] <url>
            Lists the files contained in the most current backup or backup at time. The information will be
            extracted from the signature files, not the archive data itself. Thus the whole archive does not
            have to be downloaded, but on the other hand if the archive has been deleted or corrupted, this
            command will not detect it.

        :return: returncode
        """
        target = "s3+http://{bucket}/{path}".format(**self._config.get("remote"))
        args = self._args
        action = "list-current-files"

        if self.options.get("time") is not None:
            args.extend(["--time", self.options.get("time")])

        if self.verbose:
            echo_info("Collection status of the backup in target: '{}'".format(target))

        return self._execute(action, *args, target, runtime_env=self.get_aws_secrets())

    def do_remove_older(self) -> int:
        """Remove older backup sets.

        From the docs:
        remove-older-than <time> [--force] <url>
            Delete all backup sets older than the given time. Old backup sets will not be deleted if backup sets
            newer than time depend on them. See the TIME FORMATS section for more information. Note, this action
            cannot be combined with backup or other actions, such as cleanup. Note also that --force will be
            needed to delete the files instead of just listing them.

        remove-all-but-n-full <count> [--force] <url>
            Delete all backups sets that are older than the count:th last full backup (in other words, keep the
            last count full backups and associated incremental sets). count must be larger than zero. A value
            of 1 means that only the single most recent backup chain will be kept. Note that --force will be
            needed to delete the files instead of just listing them.

        remove-all-inc-of-but-n-full <count> [--force] <url>
            Delete incremental sets of all backups sets that are older than the count:th last full backup (in
            other words, keep only old full backups and not their increments). count must be larger than zero.
            A value of 1 means that only the single most recent backup chain will be kept intact.
            Note that --force will be needed to delete the files instead of just listing them.
        """
        target = "s3+http://{bucket}/{path}".format(**self._config.get("remote"))
        args = self._args
        action = None

        if self.options.get("time") is not None:
            action = ["remove-older-than", self.options.get("time")]
        if self.options.get("all_but_n_full") is not None:
            action = ["remove-all-but-n-full", str(self.options.get("all_but_n_full"))]
        if self.options.get("all_incremental_but_n_full") is not None:
            action = [
                "remove-all-inc-but-n-full",
                str(self.options.get("all_incremental_but_n_full")),
            ]
        if action is None:
            echo_failure("Please provide a remove action")
            if self.verbose:
                print(self.options)
            sys.exit(1)

        if self.options.get("force"):
            args.append("--force")

        if self.verbose:
            echo_info("Collection status of the backup in target: '{}'".format(target))

        return self._execute(*action, *args, target, runtime_env=self.get_aws_secrets())
