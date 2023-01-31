import sys
from pathlib import Path

import click
import yaml

from duplicity_backup_s3.config import check_config_file
from duplicity_backup_s3.defaults import (
    CONFIG_FILENAME,
    CONFIG_FILEPATH,
    CONFIG_TEMPLATE_PATH,
    CONTEXT_SETTINGS,
    appdirs,
)
from duplicity_backup_s3.utils import echo_failure, echo_info, echo_success, run_as_root


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-c",
    "--config",
    help="Config file location. Alternatively set the environment variable: "
    "`DUPLICITY_BACKUP_S3_CONFIG`.",
    envvar="DUPLICITY_BACKUP_S3_CONFIG",
    default=CONFIG_FILEPATH,
)
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose", default=False)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Non interactive - be quiet - don't ask questions and create an empty "
    "configfile here in the current directory.",
    default=False,
)
def init(**options):
    """Initialise an empty configuration file."""
    # Early bailout when `quiet` flag is set
    if options.get("quiet"):
        import shutil

        shutil.copy(CONFIG_TEMPLATE_PATH, Path(Path.cwd() / CONFIG_FILENAME))
        config = check_config_file(Path(Path.cwd() / CONFIG_FILENAME), exit=True)
        if options.get("verbose"):
            echo_info(f"Initialising an empty config file in: '{config}'")
        return 0

    config_path_options = [
        ("1. Current directory", Path.cwd()),
        ("2. User configuration directory", Path(appdirs.user_config_dir)),
        (
            "3. System configuration directory (only root)",
            Path(appdirs.site_config_dir),
        ),
    ]

    echo_info("Choose the path of the configuration file:")
    echo_info("\n".join(["{} ({})".format(*o) for o in config_path_options]))
    choice = int(click.prompt("Path", default=1, type=click.Choice(["1", "2", "3"])))
    _, config_path = config_path_options[choice - 1]
    echo_success(f"you choose: {config_path}")

    # when choosing root, ensure you run as root
    if choice == 3 and not run_as_root():
        echo_failure(
            "You need to run this command again with `sudo` rights to manage "
            "the system wide configuration."
        )
        sys.exit(1)

    # when choosing current dir, let user also choose the name of the config file.
    config_filename = CONFIG_FILENAME
    if choice == 1:
        config_filename = click.prompt(
            "Filename of the configuration file", default=CONFIG_FILENAME
        )

    config = check_config_file(
        Path(config_path / config_filename), exit=False, verbose=options.get("verbose")
    )

    if config.exists() and not click.confirm(
        "Do you want to override an already existing '{}' (original will be "
        "backedup as '{}.backup'".format(config.name, config.name)
    ):
        echo_info("Exiting without overwriting current config file")
        sys.exit(1)

    if config.exists():
        echo_info("Backing up old config file.")
        deprecated_config_filename = Path(f"{config.name}.backup")
        config.replace(deprecated_config_filename)

    with CONFIG_TEMPLATE_PATH.open() as f:
        default_config = yaml.safe_load(f)

    # we can alter the default configuration here
    echo_info(
        "Please answer some basic configuration questions to initialise "
        "a working solution."
    )
    default_config["aws"]["AWS_ACCESS_KEY_ID"] = click.prompt(
        "Provide the S3 (Amazon) Access Key ID",
        default=default_config["aws"]["AWS_ACCESS_KEY_ID"],
    )
    default_config["aws"]["AWS_SECRET_ACCESS_KEY"] = click.prompt(
        "Provide the S3 (Amazon) Access Key ID",
        default=default_config["aws"]["AWS_SECRET_ACCESS_KEY"],
    )
    default_config["backuproot"] = click.prompt(
        "Backup root directory (everything under it will be backed up",
        default=default_config["backuproot"],
        type=click.Path(),
    )
    default_config["remote"]["bucket"] = click.prompt(
        "Name of the s3 bucket as backup target",
        default=default_config["remote"]["bucket"],
    )
    default_config["remote"]["path"] = click.prompt(
        "Name of the path inside the bucket", default=default_config["remote"]["path"]
    )

    # write config to disk
    with config.open("w") as fd:
        echo_info(f"Initialising an empty config file in: '{config}'")
        fd.write(yaml.dump(default_config))

    if config.exists():
        check_config_file(config)
        sys.exit(0)
    else:
        echo_failure(
            "Config file does not exist in '{}', please provide.".format(
                options.get("config")
            )
        )
        sys.exit(2)
