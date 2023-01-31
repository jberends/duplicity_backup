#!/usr/bin/env python

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
            f"Results of the run were: \n---\n{result.output}\n---",
        )
        self.assertIn("Show this message and exit.", result.output)

    def test_command_line_interface_version(self):
        result = self.runner.invoke(duplicity_backup_s3, ["--version"])
        self.assertEqual(
            result.exit_code,
            0,
            f"Results of the run were: \n---\n{result.output}\n---",
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
        self.dupe = DuplicityS3()

    def test_duplicity_remote_uri_property(self):
        """
        Testing the DuplicityS3.remote_uri property with different settings.

        The URIs are retrieved from the duplicity `--help` command from
        duplicity versions 1.2.1 and 0.7.19. The 0.7.19 is included in centos7.
        """

        # triple with endpoint, bucket, path, (optional FULL url to check against)
        endpoint_pass = {
            ("azure://container_name", "", ""),
            ("b2://account_id:application_key@bucket_name", "", "/some_dir/"),
            ("boto3+s3://", "bucket_name", "/prefix"),
            ("cf+http://container_name", "", ""),
            ("copy://user:password@other.host", "", "/some_dir"),
            ("dpbx://", "", "/some_dir"),
            ("file://", "", "/some_dir"),
            ("ftp://user:password@other.host:port", "", "/some_dir"),
            ("ftps://user:password@other.host:port", "", "/some_dir"),
            ("gdocs://user:password@other.host", "", "/some_dir"),
            ("hsi://user:password@other.host:port", "", "/some_dir"),
            ("https://ams3.digitaloceanspaces.com/", "bucketname", "/some_dir"),
            ("imap://user:password@other.host:port/", "", "some_dir"),
            ("mega://user:password@other.host/", "", "some_dir"),
            ("megav2://user:password@other.host/", "", "some_dir"),
            ("mf://user:password@other.host/", "", "some_dir"),
            ("onedrive://", "", "some_dir"),
            ("pca://", "container_name", ""),
            (
                "pydrive://user@other.host",
                "",
                "/some_dir",
                "pydrive://user@other.host/some_dir",  # full uri
            ),
            ("rclone://remote:", "", "/some_dir"),
            ("rsync://user:password@other.host:port", "", "//absolute_path"),
            ("rsync://user:password@other.host:port", "", "/relative_path"),
            (
                "rsync://user:password@other.host:port::",
                "module",
                "/some_dir",
                "rsync://user:password@other.host:port::/module/some_dir",  # full uri
            ),
            ("s3://other.host:port/", "bucket_name", "/prefix"),
            ("scp://user:password@other.host:port", "", "/some_dir"),
            ("ssh://user:password@other.host:port", "", "/some_dir"),
            ("swift://container_name", "", ""),
            ("tahoe://", "alias", "/directory"),
            ("webdav://user:password@other.host", "", "/some_dir"),
            ("webdavs://user:password@other.host", "", "/some_dir"),
            (
                "host",
                "bucket_name",
                "/prefix",
                "s3://host/bucket_name/prefix",  # full uri
            ),
            (None, "bucket", "path", "s3+http://bucket/path"),
            ("host", None, "path", "s3://host/path")
        }

        def _construct_config(triple: tuple) -> dict:
            return dict(
                dict(
                    remote=dict(
                        endpoint=triple[0],
                        bucket=triple[1],
                        path=triple[2],
                    )
                )
            )

        for triple in endpoint_pass:
            if len(triple) == 4:
                uri = triple[3]
            else:
                uri = "".join(triple)
            self.dupe._config = _construct_config(triple)
            with self.subTest(f"Testing '{uri}'"):
                self.assertEqual(uri, self.dupe.remote_uri, f"{triple} vs {uri}")
