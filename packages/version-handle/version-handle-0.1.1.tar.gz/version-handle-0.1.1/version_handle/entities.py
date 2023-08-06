# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Eason.Deng
# Github: https://github.com/holbos-deng
# Email: 2292861292@qq.com
# CreateDate: 2022/6/24 14:07
# Description:
import re


class CompareResult:
    result = 0

    def __init__(self, result):
        self.result = result

    @property
    def is_gt(self):
        return self.result == 1

    @property
    def is_lt(self):
        return self.result == 2

    @property
    def is_ge(self):
        return self.result == 1 or self.result == 0

    @property
    def is_le(self):
        return self.result == 2 or self.result == 0

    @property
    def is_equal(self):
        return self.result == 0

    def __repr__(self):
        if self.is_gt:
            return "大于"
        if self.is_ge:
            return "大于等于"
        if self.is_lt:
            return "小于"
        if self.is_le:
            return "小于等于"
        if self.is_equal:
            return "等于"


class Version:
    _v = (0, 0, 0)

    def __init__(self, v):
        self._v = re.findall(r"[a-zA-Z\d]+", v)

    @staticmethod
    def _compare(a, b):
        if a.isnumeric() and b.isnumeric():
            a = int(a)
            b = int(b)
        if a > b:
            return 1
        elif a < b:
            return 2
        return 0

    @staticmethod
    def compare(v1, v2):
        for _v1, _v2 in zip(v1, v2):
            x = Version._compare(_v1, _v2)
            if x:
                return CompareResult(x)
        return CompareResult(0)

    def __gt__(self, other):
        return Version.compare(self._v, other._v).is_gt

    def __ge__(self, other):
        return Version.compare(self._v, other._v).is_ge

    def __lt__(self, other):
        return Version.compare(self._v, other._v).is_lt

    def __le__(self, other):
        return Version.compare(self._v, other._v).is_le

    def __eq__(self, other):
        return Version.compare(self._v, other._v).is_equal
