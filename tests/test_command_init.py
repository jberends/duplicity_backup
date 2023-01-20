from click import Path

from duplicity_backup_s3.cli import duplicity_backup_s3
from duplicity_backup_s3.utils import temp_chdir
from tests.test_base import TestSetup


class TestCommandInit(TestSetup):
    def test_init_create_empty_config(self):
        with temp_chdir():
            # no config file there!
            result = self.runner.invoke(
                duplicity_backup_s3, ["init", "--quiet", "--verbose"]
            )
            self.assertEqual(result.exit_code, 0)
