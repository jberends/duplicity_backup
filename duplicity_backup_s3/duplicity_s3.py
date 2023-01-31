import os
import subprocess
import sys
import warnings
from pathlib import Path
from pprint import pprint
from typing import List, Tuple, Union
from urllib.parse import urlsplit

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
        self._config_file = None
        self._config: dict = {}
        self.options: dict = options
        if "config" in options:
            self._config_file: Path = Path(Path.cwd() / options.get("config"))
            self.read_config(path=self._config_file)
        self.verbose: bool = options.get("verbose", False)
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
        if self._get_gpg_secrets():
            runtime_env["PASSPHRASE"] = self._get_gpg_secrets().get("PASSPHRASE")
            runtime_env["GPG_KEY"] = self._get_gpg_secrets().get("GPG_KEY")
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
        Will always return a dict. The dict is empty, without any keys when
        no PASSPHRASE and/or GPG_KEY are provided.

        The PASSPHRASE and GPG_KEY are always coming from EITHER the configuration
        yaml file OR the environment and cannot be mixed. When the configuration YAML
        does not provide both, you may assume that duplicity throws an error.

        :returns: dict with 2 keys "PASSPHRASE" and "GPG_KEY" when they are provided
            otherwise an empty dict.
        """
        if "gpg" in self._config:
            return self._config.get("gpg")
        elif self.env("PASSPHRASE", default=False):
            return dict(
                PASSPHRASE=self.env("PASSPHRASE", default=""),
                GPG_KEY=self.env("GPG_KEY", default=""),
            )
        else:
            return dict()

    @property
    def _endpoint_uri(self) -> Union[str, None]:
        """
        The endpoint URI from the configuration.

        If `endpoint` is available in the `config > remote` than return this
        URI, otherwise return None. According to the configuration schema the
        `endpoint` is optionally part of the `config > remote`

        :return: remote endpoint URI or None when not configured.
        """
        return self._config["remote"].get("endpoint")

    @property
    def remote_uri(self) -> str:
        """
        The remote URL of the backup location.

        Constructed from the `config > remote` settings in the configuration yaml.

        When an `uri` is provided in the yaml it assumes that this uri is carefully
        constucted by the user and this uri is the full target uri for the duplicity
        command. It may be used as target_url or source_url in backups and restores.

        When an `endpoint` is provided the url is constructed with this url. If not
        provided the url is assumed to be on amazon s3 and a `s3+http://` is
        constructed.

        :return: remote url for the backup location.
        """
        remote = self._config["remote"]
        # fast bail when a URI is provided.
        if "uri" in self._config["remote"]:
            return remote.get("uri")

        bucket = bucket_str = self._config["remote"].get("bucket") or ""
        path = path_str = self._config["remote"].get("path") or ""
        endpoint = endpoint_str = self._config["remote"].get("endpoint") or ""

        if endpoint and bucket:
            endpoint_str = f"{endpoint}/" if not endpoint.endswith("/") else endpoint
        if not path.startswith("/"):
            if path and bucket:
                path_str = f"/{path}" if not bucket_str.endswith("/") else path
            if path and endpoint and not bucket:
                path_str = f"/{path}" if not endpoint_str.endswith("/") else path

        # construct target_uri from the '*_str'
        target_uri = "".join((endpoint_str, bucket_str, path_str))
        if not endpoint:
            target_uri = f"s3+http://{target_uri}"

        # check if endpoint has a scheme in it. If not prepend s3://
        scheme = urlsplit(target_uri).scheme
        if not scheme:
            target_uri = f"s3://{target_uri}"

        return target_uri

    def _extend_args(self, args: Union[List, None] = None) -> List:
        """
        Return extended arguments based on the most common arguments.

        The most common arguments which are added are:
        `--s3-endpoint-url`, `--encrypt-key` or `--no-encryption`, `--dry-run`

        :return: A list of arguments to add
        """
        if args is None or not isinstance(args, (List, Tuple)):
            args = self._args
        # TODO: not supported in older style duplicity (version 0.7.19 not) need
        #  to refactor to make this version dependend as the new s3:// url
        #  constructor does not work.
        # if self._endpoint_uri:
        #     args.extend(["--s3-endpoint-url", self._endpoint_uri])
        if self._get_gpg_secrets().get("GPG_KEY", False):
            args.extend(["--encrypt-key", self._get_gpg_secrets().get("GPG_KEY")])
        elif not self._get_gpg_secrets():
            args.append("--no-encryption")
        if self.dry_run:
            args.append("--dry-run")
        if self._config["remote"].get("s3-european-buckets", True):
            # Default added. May be suppressed in config.
            args.append("--s3-european-buckets")
        if self._config["remote"].get("use-new-style", True):
            # Default added. May be suppressed in config.
            args.append("--s3-use-new-style")

        # add additional argument that are passable to duplicity.
        if self._config.get("extra_args") and isinstance(
            self._config.get("extra_args"), list
        ):
            args.extend(self._config["extra_args"])
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
    def get_cludes(includes: List[str] = None, excludes: List[str] = None) -> List[str]:
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
        target = self.remote_uri
        args = self._extend_args()
        args.extend(
            [
                *DUPLICITY_BACKUP_ARGS,
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
        restore_from_url = self.remote_uri
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
            source = self.remote_uri
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
        target = self.remote_uri
        args = self._extend_args()
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
        target = self.remote_uri
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
        target = self.remote_uri
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
        target = self.remote_uri
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
