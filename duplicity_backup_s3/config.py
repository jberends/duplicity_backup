import sys
from pathlib import Path
from typing import Optional, Union

from duplicity_backup_s3.defaults import CONFIG_SCHEMA_PATH, appdirs
from duplicity_backup_s3.utils import echo_failure, echo_info


def check_config_file(
    config_file: Union[str, Path],
    path: Union[str, Path, None] = None,
    exit=True,
    verbose=False,
    testing=False,
) -> Optional[Path]:
    """
    Validate and return the full absolute Path to the config file.

    Will search of the configuration file in the following order:
    1. the current working directory
    2. the user configuration directory ('~/.config/duplicity_backup/')
    3. the system configuration directory ('~/etc/duplicity_backup/')

    :param config_file: filename and/or path to the config file
    :param path: helper path if the config_file if the config_file is not a full path
    :param exit: when exit is true, exit with return_code 2
    :param testing: in testing mode, no CLI verbosity
    :return: Path to the config file
    """
    config_path = search_config(config_file, path=path, exit=exit and not testing)

    if not config_path.exists():
        if exit:
            echo_failure(
                "Config file does not exist in '{}', please provide or "
                "create an empty one using the command `init`.".format(config_file)
            )
            sys.exit(2)
        else:
            # could be a file that does not exist
            return Path(config_path)

    # performing validation
    import yaml
    from cerberus import Validator

    validator = Validator()
    validator.allow_unknown = False
    with config_path.open() as config_fd, CONFIG_SCHEMA_PATH.open() as schema_fd:
        if not validator.validate(yaml.safe_load(config_fd), yaml.safe_load(schema_fd)):
            if not testing:
                echo_failure(
                    "The configuration file is incorrectly formatted: \n{}".format(
                        validator.errors
                    )
                )
            if exit and not testing:
                sys.exit(2)
            return validator.errors

    if verbose and not testing:
        echo_info(
            "The configuration file is successfully validated against the "
            "validation schema."
        )
    return config_path


def search_config(
    config_file: Union[str, Path],
    path: Union[str, Path, None] = None,
    exit: bool = True,
) -> Union[Path]:
    """
    Config path searched throughout the filesystem.

    Will look in current directory first, or when path is provided there.
    When the config_path is provided, then it will not search the current
    working directory but check for the config_file (filename) in the
    config_path (dir).

    Will search of the configuration file int he following order:
    1. the current working directory
    2. the user configuration directory ('~/.config/duplicity_backup/')
    3. the system configuration directory ('~/etc/duplicity_backup/')

    :param config_file: filename or full filepath (:class:`Path`) to search the
    configuration file in.
    :param path: (optional) helper path to search the configuration file in.
    :param exit: will exit with returncode 2 if the config file could not be found.
    :return: full :class:`Path` to the configuration file.
    :raises OSError: optional raise when exit is False
    """
    path = Path(path) if path is not None else path

    # Check the directly provided config_file first
    if Path(config_file).exists():
        return Path(config_file)

    # Check the current directory (or subpath in the current directory)
    elif path is None and Path(Path.cwd() / config_file).exists():
        return Path(Path.cwd() / config_file)

    # use the provided config_path to check the config_file.
    elif path is not None and Path(Path(path) / config_file).exists():
        return Path(Path(path) / config_file)

    # then search in the user config dir
    elif Path(Path(appdirs.user_config_dir) / Path(config_file).name).exists():
        # found the config_file in the user configuration directory of the app
        return Path(Path(appdirs.user_config_dir) / Path(config_file).name)

    # finally search in the /etc config dir
    elif Path(Path(appdirs.site_config_dir) / Path(config_file).name).exists():
        # found the config_file in the /etc/ configruation directory of the app
        return Path(Path(appdirs.site_config_dir) / Path(config_file).name)

    if exit:
        echo_failure(
            "Could not find the configuration file. Please give me a hint "
            "with the `--config` parameter."
        )
        sys.exit(2)
    else:
        # could be a new config_file that does not exist
        return Path(config_file)
