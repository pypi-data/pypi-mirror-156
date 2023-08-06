# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Eason.Deng
# Github: https://github.com/holbos-deng
# Email: 2292861292@qq.com
# CreateDate: 2022/6/24 14:07
# Description:
import re


class Version:
    v = (0, 0, 0)

    def __init__(self, v):
        self.v = re.findall(r"[a-zA-Z\d]+", v)

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
                return x
        return 0

    def __gt__(self, other):
        return Version.compare(self.v, other.v) == 1

    def __ge__(self, other):
        x = Version.compare(self.v, other.v)
        return x == 1 or x == 0

    def __lt__(self, other):
        return Version.compare(self.v, other.v) == 2

    def __le__(self, other):
        x = Version.compare(self.v, other.v)
        return x == 2 or x == 0

    def __eq__(self, other):
        return Version.compare(self.v, other.v) == 0
