# -*- coding: utf-8 -*-
# @Author: Bi Ying
# @Date:   2022-08-02 20:03:15
# @Last Modified by:   Bi Ying
# @Last Modified time: 2022-08-02 21:56:58
from plugin import Main

if __name__ == "__main__":
    r = Main().query("hello my love")
    print(r)

    r = Main().query("en bflm hello my love")
    print(r)
