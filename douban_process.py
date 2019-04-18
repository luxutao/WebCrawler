#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    进程方式
"""



import requests
import time
import multiprocessing

from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = 'https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start={0}&type=T'


def openurl(url):
    return requests.get(url, verify=False).content.decode()


def parse(data, tag):
    soup = BeautifulSoup(data, 'lxml')
    return [n.get('title') for n in soup.find_all(tag) if n.get('title')]


if __name__ == '__main__':
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for n in range(0, 1000, 20):
        content = pool.apply_async(parse, (openurl(url.format(n)), 'a'))
        print(n, content.get())
    pool.close()
    pool.join()
