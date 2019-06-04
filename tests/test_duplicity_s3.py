#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `duplicity_backup_s3` package."""
from pathlib import Path
from unittest import TestCase

from click.testing import CliRunner

from duplicity_backup_s3 import __version__
from duplicity_backup_s3.cli import duplicity_backup_s3


class TestDuplicity_s3(TestCase):
    """Tests for `duplicity_backup_s3` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.runner = CliRunner(env=dict(DRY_RUN="1"))

    def tearDown(self):
        """Tear down test fixtures, if any."""

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

    def test_no_config(self):
        result = self.runner.invoke(duplicity_backup_s3, "init --config foobar")
        self.assertEqual(
            result.exit_code,
            1,
            "Results of the run were: \n---\n{}\n---".format(result.output),
        )
        self.assertIn("please provide", result.output)

    def test_with_config(self):
        cfg_file = Path(Path(__file__).parent / "files" / "duplicity_backup_s3.tests.yaml")
        result = self.runner.invoke(
            duplicity_backup_s3, "incr --config={} --dry-run".format(cfg_file)
        )
        self.assertEqual(
            result.exit_code,
            0,
            "Results of the run were: \n---\n{}\n---".format(result.output),
        )


class TestNonCLI(TestCase):
    def test_duplicity(self):
        """Search the duplicity command on the platform."""
        from duplicity_backup_s3.duplicity_s3 import DuplicityS3

        self.assertTrue(DuplicityS3.duplicity_cmd())
