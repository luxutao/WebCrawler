#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    获得页面下载地址
"""

import sys
import requests

from bs4 import BeautifulSoup


try:
    url = sys.argv[1]
except IndexError:
    exit(1)


def main():
    bsoup = BeautifulSoup(requests.get(url).content, 'lxml')
    tabs = bsoup.find(class_="tabs-list")
    inputs = tabs.find_all(class_="down_url")
    for i in inputs:
        print(i['value'])


if __name__ == '__main__':
    main()
