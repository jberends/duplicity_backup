from pathlib import Path
from tempfile import NamedTemporaryFile, SpooledTemporaryFile
from unittest import TestCase

from click.testing import CliRunner

from duplicity_backup_s3.utils import check_config_file


class TestConfig(TestCase):
    def test_vanilla_config(self):
        config_yaml = """
        aws:
          AWS_ACCESS_KEY_ID: foobar_aws_key_id
          AWS_SECRET_ACCESS_KEY: foobar_aws_access_key
        backuproot: /home
        excludes:
          - _TESTFILE_TO_EXCLUDE
        includes:
          - Pictures
        remote:
          bucket: ''
          path: '__test'
        full_if_older_than: 7D
        """
        with NamedTemporaryFile(mode="w") as t:
            t.write(config_yaml)
            t.flush()
            self.assertEqual(
                check_config_file(config_file=Path(t.name), testing=True), Path(t.name)
            )

    def test_extra_key_fails(self):
        config_yaml = """
        aws:
          AWS_ACCESS_KEY_ID: foobar_aws_key_id
          AWS_SECRET_ACCESS_KEY: foobar_aws_access_key
        backuproot: /home
        excludes:
          - _TESTFILE_TO_EXCLUDE
        includes:
          - Pictures
        remote:
          bucket: ''
          path: '__test'
        full_if_older_than: 7D
        One_more_key: fail
        """
        with NamedTemporaryFile(mode="w") as t:
            t.write(config_yaml)
            t.flush()
            self.assertDictEqual(
                check_config_file(config_file=Path(t.name), testing=True),
                {"One_more_key": ["unknown field"]},
            )

    def test_optional_missing_key_succeed(self):
        config_yaml = """
        aws:
          AWS_ACCESS_KEY_ID: foobar_aws_key_id
          AWS_SECRET_ACCESS_KEY: foobar_aws_access_key
        backuproot: /home
        remote:
          bucket: ''
          path: '__test'
        full_if_older_than: 7D
        """
        with NamedTemporaryFile(mode="w") as t:
            t.write(config_yaml)
            t.flush()
            self.assertEqual(
                check_config_file(config_file=Path(t.name), testing=True), Path(t.name)
            )

    def test_required_missing_key_fails(self):
        config_yaml = """
        aws:
          AWS_ACCESS_KEY_ID: foobar_aws_key_id
          AWS_SECRET_ACCESS_KEY: foobar_aws_access_key
        backuproot: /home
        remote:
          path: '__test'
        full_if_older_than: 7D
        """
        with NamedTemporaryFile(mode="w") as t:
            t.write(config_yaml)
            t.flush()
            self.assertDictEqual(
                check_config_file(config_file=Path(t.name), testing=True),
                {"remote": [{"bucket": ["required field"]}]},
            )

    def test_incorrect_value_type_fails(self):
        config_yaml = """
        aws:
          AWS_ACCESS_KEY_ID: foobar_aws_key_id
          AWS_SECRET_ACCESS_KEY: foobar_aws_access_key
        backuproot: 1
        remote:
          bucket: ''
          path: '__test'
        full_if_older_than: 7D
        """
        with NamedTemporaryFile(mode="w") as t:
            t.write(config_yaml)
            t.flush()
            self.assertDictEqual(
                check_config_file(config_file=Path(t.name), testing=True),
                {"backuproot": ["must be of string type"]},
            )

    def test_config_from_production_success(self):
        config_yaml = """
        aws:
          AWS_ACCESS_KEY_ID: fakekey 
          AWS_SECRET_ACCESS_KEY: fakesecret
        backuproot: /opt/dir/
        includes:
          - /opt/dir/*-media
          - /opt/dir/var/archives
        excludes: 
          - "**"
        remote:
          bucket: somebucket
          path: __testpath
        """
        with NamedTemporaryFile(mode="w") as t:
            t.write(config_yaml)
            t.flush()
            self.assertEqual(
                check_config_file(config_file=Path(t.name), testing=True),
                Path(t.name),
            )
