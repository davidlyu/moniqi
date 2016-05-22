# encoding=utf-8

"""
FILE   : tools
PROJECT: moniqi
AUTHOR : bj
DATE   : 2016-05-22 19:28
"""

import sys


def check_integer(num, min_=None, max_=None):
    if not isinstance(num, int):
        raise ValueError('num is not a integer')

    cond1 = (min_ is not None) and (num < min_)
    cond2 = (max_ is not None) and (num > max_)
    if cond1 or cond2:
        raise ValueError('mum must be great than or equal to 0,'
                         'and less than or equal to 225')


def check_string(string):
    if not isinstance(string, str):
        raise ValueError('string must be a string')
