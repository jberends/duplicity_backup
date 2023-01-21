#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `duplicity_backup_s3` package."""
from pathlib import Path
from unittest import TestCase

from duplicity_backup_s3 import __version__
from duplicity_backup_s3.cli import duplicity_backup_s3
from duplicity_backup_s3.duplicity_s3 import DuplicityS3
from tests.test_base import TestSetup


class TestDuplicity_s3(TestSetup):
    """Tests for `duplicity_backup_s3` package."""

    def test_command_line_interface_help(self):
        result = self.runner.invoke(duplicity_backup_s3, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "--help",
            result.output,
            "Results of the run were: \n---\n{}\n---".format(result.output),
        )
        self.assertIn("Show this message and exit.", result.output)

    def test_command_line_interface_version(self):
        result = self.runner.invoke(duplicity_backup_s3, ["--version"])
        self.assertEqual(
            result.exit_code,
            0,
            "Results of the run were: \n---\n{}\n---".format(result.output),
        )
        self.assertIn(__version__, result.output)

    def test_with_config(self):
        cfg_file = Path(
            Path(__file__).parent / "files" / "duplicity_backup_s3.tests.yaml"
        )
        result = self.runner.invoke(
            duplicity_backup_s3, f"incr --config={cfg_file} --dry-run"
        )
        self.assertEqual(
            result.exit_code,
            0,
            f"Results of the run were: \n---\n{result}\n---",
        )


class TestNonCLI(TestCase):
    def test_duplicity(self):
        """Search the duplicity command on the platform."""
        from duplicity_backup_s3.duplicity_s3 import DuplicityS3

        self.assertTrue(DuplicityS3.duplicity_cmd())


class TestDuplicityS3Klass(TestCase):
    def setUp(self) -> None:
        self.base_config = dict(
            dict(remote=dict(bucket="foo", path="foo", endpoint="s3://"))
        )
        self.dupe = DuplicityS3()

    def test_duplicity_remote_uri_property(self):
        """Testing the DuplicityS3.remote_uri property with different settings."""
        endpoint_pass = {
            "azure://container_name",
            "b2://account_id:application_key@bucket_name/some_dir/",
            "boto3+s3://bucket_name/prefix",
            "cf+http://container_name",
            "copy://user:password@other.host/some_dir",
            "dpbx:///some_dir",
            "file:///some_dir",
            "ftp://user:password@other.host:port/some_dir",
            "ftps://user:password@other.host:port/some_dir",
            "gdocs://user:password@other.host/some_dir",
            "hsi://user:password@other.host:port/some_dir",
            "https://ams3.digitaloceanspaces.com/",
            "imap://user:password@other.host:port/some_dir",
            "mega://user:password@other.host/some_dir",
            "megav2://user:password@other.host/some_dir",
            "mf://user:password@other.host/some_dir",
            "onedrive://some_dir",
            "pca://container_name",
            "pydrive://user@other.host/some_dir",
            "rclone://remote:/some_dir",
            "rsync://user:password@other.host:port//absolute_path",
            "rsync://user:password@other.host:port/relative_path",
            "rsync://user:password@other.host:port::/module/some_dir",
            "s3+http://bucket_name/prefix",
            "s3+http://bucket_name/prefix",
            "s3://other.host:port/bucket_name/prefix",
            "scp://user:password@other.host:port/some_dir",
            "ssh://user:password@other.host:port/some_dir",
            "swift://container_name",
            "tahoe://alias/directory",
            "webdav://user:password@other.host/some_dir",
            "webdavs://user:password@other.host/some_dir",
        }

        self.dupe._config = self.base_config
        pass
