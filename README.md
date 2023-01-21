# Duplicity Backup to S3

[![image](https://img.shields.io/pypi/v/duplicity_backup_s3.svg)](https://pypi.python.org/pypi/duplicity_backup_s3)

[![image](https://img.shields.io/travis/jberends/duplicity_backup.svg)](https://travis-ci.org/jberends/duplicity_backup)

[![image](https://pyup.io/repos/github/jberends/duplicity_backup/shield.svg)](https://pyup.io/repos/github/jberends/duplicity_backup)

Duplicity backup to S3 for production servers using simple yaml file.

## License

Free software: Apache Software License 2.0

## Features

This is a duplicity command line backup wrapper that will backup to S3 that is using a validated yaml configuration file using modern and awesome CLI patterns. The commands `incremental`, `list files`, `status`, `verify`, `cleanup`, `remove` and `init` are implemented.

The primary use case to build this (yet another one) CLI wrapper for duplicity, is to be able to deploy the command in production and inject it into a `cron.daily` and having a hands-off automated backup of production servers. We use it a KE-works to automate our production server backups to Amazon S3.

## OS Dependencies

- [duplicity](http://duplicity.nongnu.org/)
- [python-boto](https://pypi.org/project/boto/) to connect to S3

## Installation

You can either install this as a system command on any operating system supporting Python 3.5 or later.

To install as global command from PyPI:

```bash
sudo python3 -m pip install duplicity-backup-s3
```

To install for your user only from PyPI enter the following commmand:

```bash
python3 -m pip install --user duplicity-backup-s3
```

To install from the git repository (latest master branch):

```bash
python3 -m pip install --user git+https://github.com/jberends/duplicity_backup.git#wheel=duplicity_backup_s3
```

### First use

To first use, you need to create a configuration yaml file. You can use the helper command `init` for that. Use the built-in help function for your enjoyment.

```bash
# help is neigh
duplicity_backup_s3 --help

# and to init the configuration YAML file
duplicity_backup_s3 init
```

It will drop you a `duplicity_backup_s3.yaml` in your current directory. That may look like this:

```yaml
aws:
  AWS_ACCESS_KEY_ID: foobar_aws_key_id  # your amazon S3 user that has write right to a backup bucket
  AWS_SECRET_ACCESS_KEY: foobar_aws_access_key  # your amazon S3 user secret
backuproot: /home  # the backup 'root' path. Everything underneath is considered for backup.
excludes:
  - "**"  # a list of exclude paths. May be '**' to exclude everything except what you include
includes:
  - /home/Pictures  # a list of includes, which are full paths
  - /home/Music
remote:
  bucket: '<an_s3_bucket>'  # S3 bucket name
  path: '__test'  # subpath within the bucket
full_if_older_than: 7D  # default is incremental, will create full backup every 7Days.
```

You can alter the configuration file to your liking. The command will check the configuration for its validity and tell you what went wrong and what you need to correct. If you made mistakes, it can be beneficial to checkout the duplicity man page for more information on that topic. However we tried to be as verbose as possible to guide you in the right direction.

### First backup

To perform your first backup, which is a full one, use the following command:

```bash
duplicity_backup_s3 incr --verbose

# or if the config is somewhere else
duplicity_backup_s3 incr --config /path/to/configuation.yaml
```

That might take time according to the size of the backup.
You can see the volumes being uploaded to your configured [S3 bucket](https://s3.console.aws.amazon.com/s3/home) using the S3 console.

To check the backup collection, list and verify the contents of the backup you may use:

```bash
# collection status
duplicity_backup_s3 status

# list all files
duplicity_backup_s3 list

# verify backup
duplicity_backup_s3 verify
```

### Remove old backups

To remove older backups, duplicity provides some commands. We implemented those in the `remove` command.

```bash
# to remove backups older than 7D
duplicity_backup_s3 remove --older-than 7D

# to remove older backup except the last 4 full backups
duplicity_backup_s3 remove --all-but-n-full 4
```

### Restore backups

To restore backup we implemented the `restore` command.

```bash
# to restore backups from yesterday to a current directory
duplicity_backup_s3 restore --time 1D

# to restore specific subdirectory from a specific date/time to a custom directory
duplicity_backup_s3 restore --dir specific_subdir \
    --time 2020-12-08T22:22:00+01:00 --target ~/a_restoredir
```

### Using this as daily backup in a cronjob

To use this in a daily cron job, you can alter the `crontab` for the user `root`

```bash
crontab -u root -e
```

You can alter the crontab in the following way

```text
# Daily backup and remove older backup
7 4 * * * /bin/duplicity_backup_s3 incr --config=/path/to/conf.yaml && /bin/duplicity_backup_s3 remove --older-than 7D --config=/path/to/conf.yaml
# | | | | +- the command to execute
# | | | +--- day of the week (0-6) Sunday=0 (*=every day)
# | | +----- month of the year (*=every month)
# | +------- day of the month (*=every day)
# +--------- hour of the day
#----------- minute in the hour
```

## Custom Endpoints

You can configure custom endpoint and custom additional arguments in the configuration yaml file. The custom endpoint can be configured in the section `remote > uri` and the additional arguments that are directly passed to duplicity can be configurated in the `extra_args` section as a list in the yaml file.

```yaml
...
remote:
    uri: "s3://ams3.digitaloceanspaces.com/bucketname/subpath"
extra_args:
    - --some
    - --additional
    - --arguments
    - --here=3
```

## TODO

- [x] implement appdirs for default configuration file placement
- [x] implement restore for restoring
- [x] Allow for custom s3 storage endpoints. Included in v1.2.0 with thanks to @denismatveev
- [x] If requested migrate `--s3-european-buckets` to configuration file
- [x] If requested implement GPG/Encryption capabilities. Possibly reusing code of `kecpkg-tools` to manage certificates. Included in v1.2.0 with thanks at @denismatveev


## Credits

- This package was inspired by the great work done by the duplicity team, back in the days.
- This package was inspired by the great amount of bash code by the [duplicity_backup.sh](https://github.com/zertrin/duplicity-backup.sh) project.
- This package is thankful on my knees to the great work done by the Authors and contributors behind the [Click](https://click.palletsprojects.com/en/7.x/) project, packing tons of CLI awesomeness since 2014.
- This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
