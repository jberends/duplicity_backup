# Changelog

## v1.1.0 (UNRELEASED)

* :star: Added GPG encryption possibilities. Thanks to @denismatveev. (#5)
* :star: Added the ability to use custom S3 endpoints. Now it does not default to amazon S3 and you can use S3 compatible storage targets such as digitalocean (tested on Digital Ocean). Thanks to @denismatveev. (#5)
* :+1: Improved `init` command to add a flag `--quiet` for less chatty way of initialisation of the config file. (#8)
* :+1: Thorough spring cleanup. Dropped support for Python releases below 3.7. `Black`-ened, `pyupgrade`-ed, `isort`-ed the codebase. Fixed tests and added tests for newer python releases. Switched to dependabot for dependency management.  (#8)

## v1.1.0 (8DEC20)

* added restore command implementation.

## v1.0.2 (3APR20)

* Added appdirs to the setup.py requirements.

## v1.0.1 (UNRELEASED)

Not released to the public.

## v1.0.0 (16DEC19)

First production release.

* implemented appdirs, such that the configuration file can be safely placed and located from a known configuration directory on disk.
* added `remove` command to remove collections from the backup target after a specified time. Please consult the `duplicity_backup_s3 remove --help` documentation for guidance.
* added `init` command to initialise the configuration in an interactive fashion for users.
* various development improvements, e.g. GitHub actions for testing and publishing to PyPI; removed all flake8 warnings and pydocstyle errors. Added pre-commit hooks. Code is A++ grade now.

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
