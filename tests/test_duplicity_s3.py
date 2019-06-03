#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `duplicity_backup_s3` package."""


import unittest
from click.testing import CliRunner

from duplicity_backup_s3 import duplicity_backup_s3
from duplicity_backup_s3 import __main__


class TestDuplicity_s3(unittest.TestCase):
    """Tests for `duplicity_backup_s3` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(__main__.main)
        assert result.exit_code == 0
        assert 'duplicity_backup_s3.cli.main' in result.output
        help_result = runner.invoke(__main__.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
