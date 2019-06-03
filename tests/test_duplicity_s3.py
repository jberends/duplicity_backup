#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `duplicity_backup_s3` package."""
from test.support import EnvironmentVarGuard
from unittest import TestCase

from click.testing import CliRunner

from duplicity_backup_s3 import cli, __version__


class TestDuplicity_s3(TestCase):
    """Tests for `duplicity_backup_s3` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.runner = CliRunner(env=dict(DRY_RUN=1))


    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_command_line_interface_help(self):
        result = self.runner.invoke(cli.main, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "--help",
            result.output,
            "Results of the run were: \n---\n{}\n---".format(result.output),
        )
        self.assertIn("Show this message and exit.", result.output)

    def test_command_line_interface_version(self):
        result = self.runner.invoke(cli.main, ["--version"])
        self.assertEqual(
            result.exit_code,
            0,
            "Results of the run were: \n---\n{}\n---".format(result.output),
        )
        self.assertIn(__version__, result.output)

    def test_no_config(self):
        result = self.runner.invoke(cli.main, "--config foobar")
        self.assertEqual(
            result.exit_code,
            2,
            "Results of the run were: \n---\n{}\n---".format(result.output),
        )
        self.assertIn("please provide", result.output)

    def test_with_config(self):

        result = self.runner.invoke(
            cli.main, "--config='duplicity_backup_s3.tests.yaml' --dry-run"
        )
        self.assertEqual(
            result.exit_code,
            0,
            "Results of the run were: \n---\n{}\n---".format(result.output),
        )


class TestNonCLI(TestCase):
    def test_duplicity(self):
        """Test something."""
        from duplicity_backup_s3.duplicity_s3 import duplicity_cmd

        self.assertTrue(duplicity_cmd())
