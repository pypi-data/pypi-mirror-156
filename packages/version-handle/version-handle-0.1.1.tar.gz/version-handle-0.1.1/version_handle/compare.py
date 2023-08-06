# -*-coding:utf-8-*-
# Author: Eason.Deng
# Github: https://github.com/holbos-deng
# Email: 2292861292@qq.com
# CreateDate: 2022/5/23 14:42
# Description:
import re
from .entities import CompareResult, Version


def compare(v1, v2):
    v1_obj: Version = Version(v1)
    v2_obj: Version = Version(v2)
    return Version.compare(v1_obj._v, v2_obj._v)
