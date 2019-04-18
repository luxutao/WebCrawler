#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    下载必应首页背景
"""


import re
import os
import time
import requests
import json


def openurl():
    """获得返回的json"""
    timestamp = int(round(time.time() * 1000))
    url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&nc={timestamp}&pid=hp'.format(
        timestamp=timestamp)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'referer': 'https://cn.bing.com/'
    }
    return requests.get(url, headers=headers).content.decode()


def main():
    """保存文件"""
    path = os.path.dirname(os.path.abspath(__file__))
    data = json.loads(openurl()).get('images')[0]
    desc = data.get('copyright')
    download_url = data.get('url')
    filename = os.path.basename(download_url)
    with open(path + '/' + filename, 'wb') as f:
        f.write(requests.get('https://cn.bing.com/' + download_url).content)


if __name__ == '__main__':
    main()
