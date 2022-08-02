# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2022-08-02 20:03:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2022-08-03 02:11:22
import os
from pathlib import Path

from dotenv import load_dotenv

setting_pyfile = Path(__file__).resolve()
pludir = setting_pyfile.parent
basedir = pludir.parent

dotenv_path = basedir / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# The default value can work, if no user config.
CONFIG = os.getenv("CONFIG", "default config")
LOCAL = os.getenv("local", "zh")

TRANSLATIONS_PATH = basedir / "plugin/translations"
ICON_PATH = "assets/favicon.ico"
