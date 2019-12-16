from unittest import TestCase

from click.testing import CliRunner


class TestSetup(TestCase):
    def setUp(self):
        """Set up test fixtures, if any."""
        self.runner = CliRunner(env=dict(DRY_RUN="true"))

    def tearDown(self):
        """Tear down test fixtures, if any."""
