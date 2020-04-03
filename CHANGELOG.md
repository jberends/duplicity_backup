# Changelog

## v1.0.2 (3APR20)

* Added appdirs to the setup.py requirements.

## v1.0.1 (UNLRELEASED)

Not released to the public.

## v1.0.0 (16DEC19)

First production release.

* implemented appdirs, such that the configuration file can be safely placed and located from a known configuration directory on disk.
* added `remove` command to remove collections from the backup target after a specified time. Please consult the `duplicity_backup_s3 remove --help` documentation for guidance.
* added `init` command to initialise the configuration in an interactive fashion for users.
* various development improvements, eg Github actions for testing and publishing to PyPI; removed all flake8 warnings and pydocstyle errors. Added pre-commit hooks. Code is A++ grade now.

## v0.5.0 (5JUN19)

First initial public release.

* commands `incr`, `list`, `status`, `verify`, `cleanup` implemented.
* added yaml schema check for the configuration file.

## v0.2.0 (3JUN19)

Internal release.

* migrated to command structure. Now offers `incr` and `init`

## v0.1.0 (3JUN19)

Internal release.

* First release on PyPI.
