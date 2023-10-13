# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2022-08-02 20:03:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-10-13 15:14:36
import os
from pathlib import Path


setting_pyfile = Path(__file__).resolve()
pludir = setting_pyfile.parent
basedir = pludir.parent

# The default value can work, if no user config.
CONFIG = os.getenv("CONFIG", "default config")
LOCAL = os.getenv("local", "zh")

TRANSLATIONS_PATH = basedir / "translations"
ICON_PATH = basedir / "assets" / "favicon.ico"
