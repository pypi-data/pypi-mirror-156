# -*-coding:utf-8-*-
# Author: Eason.Deng
# Github: https://github.com/holbos-deng
# Email: 2292861292@qq.com
# CreateDate: 2022/5/23 14:42
# Description:
from typing import Union


def get(vs: list):
    if isinstance(vs, Union[list, tuple]):
        return ".".join((str(x) for x in vs))
    return str(vs)
