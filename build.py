# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2023-05-15 13:34:28
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-10-13 15:50:13
import shutil
import argparse
import subprocess
from pathlib import Path


def run_cmd(cmd: list[str]):
    """
    Run command in shell
    """
    return subprocess.run(cmd, check=True)


def build_production(version):
    run_cmd(["pyinstaller", "run.spec", "--noconfirm"])
    # copy plugin.json and SettingsTemplate.yaml to dist
    dist_dir = Path("dist/run")
    plugin_json = Path("plugin.json")
    settings_template = Path("SettingsTemplate.yaml")
    assets_dir = Path("assets")
    shutil.copy(plugin_json, dist_dir)
    shutil.copy(settings_template, dist_dir)
    shutil.copytree(assets_dir, dist_dir / "assets", dirs_exist_ok=True)


parser = argparse.ArgumentParser(description="Build software.")
parser.add_argument("-v", "--version", default="0.0.1", help="version number, default: 0.0.1")
parser.add_argument(
    "-t", "--type", default="production", help="build type: development(d) or production(p) or frontend(f)"
)
args = parser.parse_args()
if args.type == "p" or args.type == "production":
    build_production(args.version)
elif args.type == "d" or args.type == "development":
    pass
