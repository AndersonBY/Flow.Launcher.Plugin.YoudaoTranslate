# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2022-08-02 20:03:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2023-10-13 15:12:59
import sys
import os


def main():
    plugin_root = sys.argv[0]
    os.chdir(os.path.dirname(os.path.abspath(plugin_root)))

    from plugin.main import YoudaoTranslate

    youdao_translate = YoudaoTranslate()
    youdao_translate.run()


if __name__ == "__main__":
    main()
