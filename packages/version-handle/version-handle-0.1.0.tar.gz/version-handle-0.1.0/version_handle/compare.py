# -*-coding:utf-8-*-
# Author: Eason.Deng
# Github: https://github.com/holbos-deng
# Email: 2292861292@qq.com
# CreateDate: 2022/5/23 14:42
# Description:
import re


class CompareResult:
    result = 0

    def __init__(self, result):
        self.result = result

    @property
    def is_more(self):
        return self.result == 1

    @property
    def is_less(self):
        return self.result == 2

    @property
    def is_equal(self):
        return self.result == 0

    def __repr__(self):
        if self.is_more:
            return "大于"
        if self.is_less:
            return "小于"
        if self.is_equal:
            return "等于"


def _compare(a, b):
    if a.isnumeric() and b.isnumeric():
        a = int(a)
        b = int(b)
    if a > b:
        return 1
    elif a < b:
        return 2
    return 0


def compare(v1, v2):
    v1s = re.findall(r"[a-zA-Z\d]+", v1)
    v2s = re.findall(r"[a-zA-Z\d]+", v2)
    for _v1, _v2 in zip(v1s, v2s):
        x = _compare(_v1, _v2)
        if x:
            return CompareResult(x)
    return CompareResult(0)
