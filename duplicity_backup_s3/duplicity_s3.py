from __future__ import annotations

import os
import subprocess
import sys
import warnings
from pathlib import Path
from pprint import pprint
from typing import List

import yaml
from envparse import env

from duplicity_backup_s3.defaults import (
    DUPLICITY_BACKUP_ARGS,
    DUPLICITY_BASIC_ARGS,
    DUPLICITY_DEBUG_VERBOSITY,
    DUPLICITY_MORE_VERBOSITY,
    DUPLICITY_VERBOSITY,
    FULL_IF_OLDER_THAN,
    NEED_SUBPROCESS_SHELL,
)
from duplicity_backup_s3.utils import echo_failure, echo_info

# /bin/duplicity
#   -v3
#   --dry-run
#   --full-if-older-than 7D
#   --s3-use-new-style
#   --s3-european-buckets
#   --exclude-device-files
#   --include=/opt/ke-chain/*-media
#   --include=/opt/ke-chain/var/archives
#   --exclude=**
#   /opt/ke-chain/   # src
#   s3://kew-prod-backup-target/kec-prod23/  # target


class DuplicityS3:
    """
    Main object for Duplicity S3 Commands.

    :ivar options: arguments provided to the class
    :ivar verbose: verbosity level
    :ivar dry_run: boolean flag to do dry_run only
    :ivar env: environment object from parse environment
    """

    def __init__(self, **options):
        """Initiate of the DuplicityS3 object with options.

        :param options: dictionary with options.
        :type options: Dict[Any:Any]
        """
        # setting environment
        self.env = env
        self._config_file: Path = Path(Path.cwd() / options.get("config"))
        self._config: dict = {}  # placeholder where the configuration is read in
        self.options: dict = options
        self.read_config(path=self._config_file)
        self.verbose: bool = options.get("verbose", False)
        self.__gpg_passphrase: str = self._get_gpg_secrets().get("PASSPHRASE")
        self.__gpg_key: str = self._get_gpg_secrets().get("GPG_KEY")
        # in case of verbosity be more than 3 verbose
        duplicity_verbosity: int = (
            DUPLICITY_MORE_VERBOSITY if options.get("verbose") else DUPLICITY_VERBOSITY
        )
        if options.get("debug"):
            duplicity_verbosity = DUPLICITY_DEBUG_VERBOSITY
            self.verbose = True

        self._args = [f"-v{duplicity_verbosity}"] + DUPLICITY_BASIC_ARGS  # type: List

        self.dry_run: bool = options.get("dry_run", False)

        with warnings.catch_warnings():  # catch the warnings that env puts out.
            warnings.simplefilter("ignore", UserWarning)
            self.env.read_envfile()

    def __runtime_env(self) -> dict:
        runtime_env = self._get_aws_secrets()
        if self.__gpg_passphrase:
            runtime_env["PASSPHRASE"] = self.__gpg_passphrase
            runtime_env["GPG_KEY"] = self.__gpg_key
        return runtime_env

    def read_config(self, path: Path = None) -> None:
        """Read the config file.

        Stores the configuration in the protected variable `self._config`.
        """
        if path is None:
            path = self._config_file
        if not path.exists():
            raise ValueError(f"Could not find the configuration file in path '{path}'")

        self._config = {}  # type: ignore
        with self._config_file.open() as fd:
            self._config = yaml.safe_load(fd)

    def _get_aws_secrets(self) -> dict:
        """AWS secrets either from the environment or from the configuration file."""
        if "aws" in self._config:
            return self._config.get("aws")  # type: ignore
        else:
            return dict(
                AWS_ACCESS_KEY_ID=self.env("AWS_ACCESS_KEY_ID", default=""),
                AWS_SECRET_ACCESS_KEY=self.env("AWS_SECRET_ACCESS_KEY", default=""),
            )

    def _get_gpg_secrets(self) -> dict:
        """GPG passphrase and public key to encrypt files on remote system.

        Either from the environment or from the configuration file.
        """
        if "gpg" in self._config:
            return self._config.get("gpg")
        else:
            return dict(
                PASSPHRASE=self.env("PASSPHRASE", default=""),
                GPG_KEY=self.env("GPG_KEY", default=""),
            )

    @property
    def _endpoint_uri(self) -> str | None:
        """
        The endpoint URI from the configuration.

        If `endpoint` is available in the `config > remote` than return this
        URI, otherwise return None. According to the configuration schema the
        `endpoint` is optionally part of the `config > remote`

        :return: remote endpoint URI or None when not configured.
        """
        return self._config["remote"].get("endpoint")

    def _extend_args(self, args: list | None = None) -> list:
        """
        Return extended arguments based on the most common arguments.

        The most common arguments which are added are:
        `--s3-endpoint-url`, `--encrypt-key` or `--no-encryption`, `--dry-run`

        :return: A list of arguments to add
        """
        if args is None or not isinstance(args, (list, tuple)):
            args = self._args
        if self._endpoint_uri:
            args.extend(["--s3-endpoint-url", self._endpoint_uri])
        if self.__gpg_key:
            args.extend(["--encrypt-key", self.__gpg_key])
        elif not self.__gpg_key and not self.__gpg_passphrase:
            args.append("--no-encryption")
        if self.dry_run:
            args.append("--dry-run")
        return args

    def _execute(self, *cmd_args, runtime_env: dict = None) -> int:
        """Execute the duplicity command."""
        command = [self.duplicity_cmd(), *cmd_args]

        if self.verbose:
            print("command used:")
            command_str = " ".join(command)
            print(f"   {command_str}")
            print("environment:")
            pprint(
                [
                    f"{k} = {v}"
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
                "The duplicity command exited with an error. "
                "Command may not have succeeded."
            )
            if self.verbose:
                echo_info(f"More information on the error:\n{e.output}")
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

    @staticmethod
    def get_cludes(includes: list[str] = None, excludes: list[str] = None) -> list[str]:
        """
        Get includes or excludes command arguments.

        :param includes: list of file includes (absolute paths, not relative from root)
        :param excludes: list of file excludes (absolute paths, not relative from root)
        :return:
        """
        arg_list = []
        if includes:
            arg_list.extend([f"--include={path}" for path in includes])
        if excludes:
            arg_list.extend([f"--exclude={path}" for path in excludes])
        return arg_list

    def do_incremental(self) -> int:
        """
        Incremental duplicity Backup.

        :return: error code
        """
        action = "incr"
        source = self._config.get("backuproot")
        target = "s3://{bucket}/{path}".format(
            **self._config.get("remote")
        )  # type: ignore
        args = self._extend_args()
        args.extend(
            [
                DUPLICITY_BACKUP_ARGS,
                "--full-if-older-than",
                self._config.get("full_if_older_than", FULL_IF_OLDER_THAN),
                *self.get_cludes(
                    includes=self._config.get("includes"),
                    excludes=self._config.get("excludes"),
                ),
            ]
        )

        return self._execute(
            action, *args, source, target, runtime_env=self.__runtime_env()
        )

    def do_restore(self) -> int:
        """Restore the backup.

        From the duplicity man page:
        restore [--file-to-restore <relpath>] [--time <time>] <url> <target_folder>
              You can restore the full monty or selected folders/files from
              a specific time. Use the relative path as it is printed by
              list-current-files. Usually not needed as duplicity enters
              restore mode when it detects that the URL comes before the
              local folder.

        :return: return_code of duplicity
        """
        action = "restore"
        restore_from_url = "s3://{bucket}/{path}".format(
            **self._config.get("remote")
        )  # type: ignore
        target = self.options.get("target")
        args = self._extend_args()

        if self.options.get("file") is not None:
            args.extend(["--file-to-restore", self.options.get("file")])

        if self.options.get("time") is not None:
            args.extend(["--time", self.options.get("time")])

        if self.verbose:
            echo_info(f"restoring backup in directory: {target}")

        return self._execute(
            action, *args, restore_from_url, target, runtime_env=self.__runtime_env()
        )

    def do_verify(self) -> int:
        """Verify the backup.

        From the duplicity man page:
        Verify [--compare-data] [--time <time>] [--file-to-restore <rel_path>]
          <url> <local_path>
            Restore backup contents temporarily file by file and compare against
            the local path’s contents. Duplicity will exit with a non-zero error
            level if any files are different. On verbosity level info (4) or
            higher, a message for each file that has changed will be logged.

            The --file-to-restore option restricts verify to that file or folder.
            The --time option allows to select a backup to verify against.
            The --compare-data option enables data comparison.

        :return: return_code of duplicity
        """
        from duplicity_backup_s3.utils import temp_chdir

        with temp_chdir() as target:
            source = "s3://{bucket}/{path}".format(
                **self._config.get("remote")
            )  # type: ignore
            action = "verify"
            args = self._extend_args()

            if self.options.get("file") is not None:
                args.extend(["--file-to-restore", self.options.get("file")])

            if self.options.get("time") is not None:
                args.extend(["--time", self.options.get("time")])

            if self.verbose:
                echo_info(f"verifying backup in directory: {target}")

            return self._execute(
                action, *args, source, target, runtime_env=self.__runtime_env()
            )

    def do_cleanup(self) -> int:
        """
        Cleanup of dirty remote.

        From the duplicity manpage:
        cleanup [--force] [--extra-clean] <url>
            Delete the extraneous duplicity files on the given backend.
            Non-duplicity files, or files in complete data sets will not
            be deleted. This should only be necessary after a duplicity session
            fails or is aborted prematurely. Note that --force will be
            needed to delete the files instead of just listing them.

        :return: returncode
        """
        target = "s3://{bucket}/{path}".format(
            **self._config.get("remote")
        )  # type: ignore
        args = self._extend_args()
        if self._endpoint_uri:
            args.extend(["--s3-endpoint-url", self._endpoint_uri])

        action = "cleanup"

        if self.options.get("force"):
            args.append("--force")

        if self.verbose:
            echo_info(f"Cleanup the backup in target: '{target}'")

        return self._execute(action, *args, target, runtime_env=self.__runtime_env())

    def do_collection_status(self) -> int:
        """
        Check the status of the collections in backup.

        From the docs:
        collection-status <url>
            Summarize the status of the backup repository by printing the chains
            and sets found, and the number of volumes in each.

        :return: returncode
        """
        target = "s3://{bucket}/{path}".format(
            **self._config.get("remote")
        )  # type: ignore
        action = "collection-status"
        args = self._extend_args()

        if self.verbose:
            echo_info(f"Collection status of the backup in target: '{target}'")

        return self._execute(action, *args, target, runtime_env=self.__runtime_env())

    def do_list_current_files(self) -> int:
        """
        List current files included in the backup.

        from the docs:
        list-current-files [--time <time>] <url>
            Lists the files contained in the most current backup or backup at
            time. The information will be extracted from the signature files,
            not the archive data itself. Thus, the whole archive does not have
            to be downloaded, but on the other hand if the archive has been
            deleted or corrupted, this command will not detect it.

        :return: returncode
        """
        target = "s3://{bucket}/{path}".format(
            **self._config.get("remote")
        )  # type: ignore
        args = self._extend_args()
        action = "list-current-files"

        if self.options.get("time") is not None:
            args.extend(["--time", self.options.get("time")])

        if self.verbose:
            echo_info(f"Collection status of the backup in target: '{target}'")

        return self._execute(action, *args, target, runtime_env=self.__runtime_env())

    def do_remove_older(self) -> int:
        """Remove older backup sets.

        From the docs:
        remove-older-than <time> [--force] <url>
            Delete all backup sets older than the given time. Old backup
            sets will not be deleted if backup sets newer than time depend
            on them. See the TIME FORMATS section for more information.
            Note, this action cannot be combined with backup or other
            actions, such as cleanup. Note also that --force will be needed
            to delete the files instead of just listing them.

        remove-all-but-n-full <count> [--force] <url>
            Delete all backups sets that are older than the count:th last
            full backup (in other words, keep the last count full backups
            and associated incremental sets). count must be larger than zero.
            A value of 1 means that only the single most recent backup chain
            will be kept. Note that --force will be needed to delete the
            files instead of just listing them.

        remove-all-inc-of-but-n-full <count> [--force] <url>
            Delete incremental sets of all backups sets that are older than
            the count:th last full backup (in other words, keep only old full
            backups and not their increments). count must be larger than zero.
            A value of 1 means that only the single most recent backup chain
            will be kept intact. Note that --force will be needed to delete
            the files instead of just listing them.
        """
        target = "s3://{bucket}/{path}".format(
            **self._config.get("remote")
        )  # type: ignore
        args = self._extend_args()
        action = None

        if self.options.get("time") is not None:
            action = ["remove-older-than", self.options.get("time")]
        if self.options.get("all_but_n_full") is not None:
            action = ["remove-all-but-n-full", str(self.options.get("all_but_n_full"))]
        if self.options.get("all_incremental_but_n_full") is not None:
            action = [
                "remove-all-inc-of-but-n-full",
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
            echo_info(f"Collection status of the backup in target: '{target}'")

        return self._execute(*action, *args, target, runtime_env=self.__runtime_env())
