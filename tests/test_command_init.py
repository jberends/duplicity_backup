from duplicity_backup_s3.cli import duplicity_backup_s3
from tests.test_base import TestSetup


class TestCommandInit(TestSetup):
    def test_init_create_empty_config(self):
        with self.runner.isolated_filesystem():
            # no config file there!
            result = self.runner.invoke(duplicity_backup_s3, ["init"])
            self.assertEqual(result.exit_code, 0)
