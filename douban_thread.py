#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    线程方式
"""


import requests
import time
import threading

from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = 'https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start={0}&type=T'


def openurl(url):
    return requests.get(url, verify=False).content.decode()


def parse(data):
    dd = BeautifulSoup(data, 'lxml')
    return [n.get('title') for n in dd.find_all('a') if n.get('title')]


def main():
    for n in range(0, 1000, 20):
        content = parse(openurl(url.format(n)))
        print(n, content)


if __name__ == '__main__':
    t = threading.Thread(target=main, name='loop')
    t.start()
    t.join()
