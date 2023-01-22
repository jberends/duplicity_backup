import os
import platform
from pathlib import Path

from appdirs import AppDirs

# default config file name

CONFIG_FILENAME = "duplicity_backup_s3.yaml"
CONFIG_FILEPATH = Path.cwd() / CONFIG_FILENAME

# Schema to check config file against
CONFIG_SCHEMA_FILENAME = "config_schema.yaml"
CONFIG_SCHEMA_PATH = Path(Path(__file__).parent / "files" / CONFIG_SCHEMA_FILENAME)

# Default config file to initialise
CONFIG_TEMPLATE_FILENAME = "config.template.yaml"
CONFIG_TEMPLATE_PATH = Path(Path(__file__).parent / "files" / CONFIG_TEMPLATE_FILENAME)

FULL_IF_OLDER_THAN = "7D"
DUPLICITY_BASIC_ARGS = ["--s3-use-new-style"]
DUPLICITY_BACKUP_ARGS = ["--asynchronous-upload", "--exclude-device-files"]
DUPLICITY_VERBOSITY = 3
DUPLICITY_MORE_VERBOSITY = DUPLICITY_VERBOSITY + 1
DUPLICITY_DEBUG_VERBOSITY = 5

# helpers for platform specific stuff
__platform = platform.system()
ON_LINUX = os.name == "posix" or __platform == "Linux"
ON_MACOS = os.name == "mac" or __platform == "Darwin"
ON_WINDOWS = NEED_SUBPROCESS_SHELL = os.name == "nt" or __platform == "Windows"

# Click defaults
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 88}
UNKNOWN_OPTIONS = {"ignore_unknown_options": True}.update(
    CONTEXT_SETTINGS
)  # type: ignore

os.environ["XDG_CONFIG_DIRS"] = "/etc:/usr/local/etc"
appdirs = AppDirs(appname="duplicity_backup", appauthor="jochem")
