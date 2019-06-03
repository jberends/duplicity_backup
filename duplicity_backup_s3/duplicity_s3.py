# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path
from pprint import pprint
from typing import Dict

import yaml
from envparse import env, Env

from duplicity_backup_s3.defaults import (
    FULL_IF_OLDER_THAN,
    DUPLICITY_DEFAULT_ARGS,
    DUPLICITY_VERBOSITY,
    NEED_SUBPROCESS_SHELL,
)


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
        self.read_config(path=self._config_file)
        self.verbose = options.get('verbose', False)
        # in case of verbosity be more than 3 verbose
        duplicity_verbosity = (
            DUPLICITY_VERBOSITY + 1 if options.get("verbose") else DUPLICITY_VERBOSITY
        )

        self._args = [
            "-v{}".format(duplicity_verbosity),
            "--full-if-older-than",
            str(FULL_IF_OLDER_THAN),
        ] + DUPLICITY_DEFAULT_ARGS

        self.dry_run = options.get("dry_run", False)

    @property
    def env(self) -> Env:
        """Read the `.env` file."""
        self._env = read_env()
        return self._env

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
                AWS_ACCESS_KEY_ID=self.env("AWS_ACCESS_KEY_ID")
                or self._config.get("aws"),
                AWS_SECRET_ACCESS_KEY=self.env("AWS_SECRET_ACCESS_KEY"),
            )

    def do_incremental(self):
        """
        Incremental duplicity Backup.

        :return: error code
        """
        source = self._config.get("backuproot")
        target = "s3+http://{bucket}/{path}".format(**self._config.get("remote"))
        args = self._args
        runtime_env = self.get_aws_secrets()
        action = "inc"

        if self.dry_run:
            args.append("--dry-run")

        command = [duplicity_cmd(), action, *args, source, target]
        if self.verbose:
            print('command used:')
            pprint(command)

        # execute duplicity command
        self.last_results = subprocess.run(command, shell=NEED_SUBPROCESS_SHELL, env=runtime_env)

        return self.last_results.returncode


def read_env(env_filename=None):
    """
    Read the env file.

    Will search for the .env file in this path or one path above.

    :param env_filename: None or path to env file (can be name otherwise)
    :return: :class:`Env` object.
    """
    return env.read_envfile(env_filename)


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
