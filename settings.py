# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2022-08-02 20:03:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2022-08-03 02:32:42
import os
from pathlib import Path

from dotenv import load_dotenv


setting_pyfile = Path(__file__).resolve()
base_dir = setting_pyfile.parent
plugin_dir = base_dir / "plugin"

dotenv_path = base_dir / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)


# The default value can work, if no user config.
CONFIG = os.getenv("CONFIG", "default config")
LOCAL = os.getenv("local", "zh")


# the information of package
__package_name__ = "YoudaoTranslate"
__version__ = "1.0.0"
__short_description__ = "Translate between any languages supported by Youdao"
GITHUB_USERNAME = "AndersonBY"


readme_path = base_dir / "README.md"
try:
    __long_description__ = open(readme_path, "r").read()
except:
    __long_description__ = __short_description__


# extensions
TRANSLATIONS_PATH = base_dir / "plugin/translations"

# plugin.json
PLUGIN_ID = "6f831f62789e4b1c9b06af149f063958"
ICON_PATH = "assets/favicon.ico"
PLUGIN_AUTHOR = "AndersonBY"
PLUGIN_ACTION_KEYWORD = "yd"
PLUGIN_PROGRAM_LANG = "python"
PLUGIN_EXECUTE_FILENAME = "main.py"
PLUGIN_ZIP_NAME = f"{__package_name__}-{__version__}.zip"
PLUGIN_URL = "https://github.com/AndersonBY/Flow.Launcher.Plugin.YoudaoTranslate"
PLUGIN_URL_SOURCE_CODE = "https://github.com/AndersonBY/Flow.Launcher.Plugin.YoudaoTranslate"
PLUGIN_URL_DOWNLOAD = (
    f"{PLUGIN_URL_SOURCE_CODE}/releases/download/v{__version__}/Flow.Launcher.Plugin.YoudaoTranslate.zip"
)
