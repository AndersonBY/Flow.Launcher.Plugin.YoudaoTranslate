# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2022-08-02 20:03:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-10-13 15:12:59
import os
import sys
from pathlib import Path


def main():
    plugin_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(plugin_root / "lib"))
    os.chdir(plugin_root)

    from plugin.main import YoudaoTranslate

    youdao_translate = YoudaoTranslate()
    youdao_translate.run()


if __name__ == "__main__":
    main()
