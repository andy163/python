# -*- coding=utf8 -*-
"""
    常量定义
"""
import  settings
class Gender(object):
    """
    性别定义
    """
    MALE = '男'
    FEMALE = '女'


class People(object):
    """
    人员类型
    """
    Followee = 1
    Follower = 2


HEADER = {
    'Host': 'www.zhihu.com',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Accept': '*/*',
    'Origin': 'https://www.zhihu.com',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': settings.USER_AGENT,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
}

