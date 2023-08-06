#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/27 12:12
# @Author  : lj
# @File    : date_conversion.py
import time


def timestamp_to_time(timestamp:int or str=None) -> str:
    """
    时间戳转换成时间
    :param timestamp: 时间戳
    :return: 时间格式字符串
    """

    if timestamp:
        timestamp = int(timestamp)
        timestamp_str = str(timestamp)
        nu = len(timestamp_str) - 10
        if nu > 0:
            timestamp = int(timestamp_str[:10])
        elif nu < 0:
            timestamp_str = str(timestamp) + '0000000000'
            timestamp = int(timestamp_str[:10])
        else:
            pass
    else:
        timestamp = time.time()

    time_local = time.localtime(timestamp)
    dt = time.strftime('%Y-%m-%d %H:%M:%S',time_local)
    return dt

def now_timestamp(number:int=13) -> int:
    """
    获取当前时间戳
    :param number: 时间戳位数（输入为int类型）
    :return:int类型时间戳
    """
    d = True
    if number == 10:
        return int(time.time())
    else:
        if number > 10:
            d = False
        if d:
            w = 10 - number
        else:
            w = number - 10
        t = ['1']
        for i in range(w):
            t.append('0')
        time_ = ''.join(t)
        multiple = int(time_)
        if d:
            return int(time.time() / multiple)
        else:
            return int(time.time() * multiple)


if __name__ == '__main__':
    """获取当前时间戳"""
    # print(now_timestamp(10))
    # print(now_timestamp())
    """时间戳转为时间"""
    aa =1656311250
    a ='1656311250651'
    print(timestamp_to_time(aa))
    print(timestamp_to_time(a))



    pass