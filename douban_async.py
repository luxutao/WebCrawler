#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    异步方式
"""


import requests
import time
import asyncio

from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = 'https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start={0}&type=T'


async def openurl(url, n):
    body = requests.get(url, verify=False).content.decode()
    await parse(body, n)


async def parse(data, n):
    soup = BeautifulSoup(data, 'lxml')
    content = [block.get('title')
               for block in soup.find_all('a') if block.get('title')]
    print(n, content)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [openurl(url.format(n), n) for n in range(0, 1000, 20)]
    loop.run_until_complete(asyncio.wait(tasks))
