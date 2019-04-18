#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    同步alpha.wallhaven.cc壁纸
"""


import re
import os
import time
import json
import random
import logging
import asyncio

import requests
import pymysql

from bs4 import BeautifulSoup
from datetime import datetime


async def openurl(url):
    """获得返回的json"""

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }
    return requests.get(url, headers=headers).content.decode()


async def getfirstpage(url, path, animetype):
    returncontent = await openurl(url)
    section = BeautifulSoup(returncontent, 'lxml')
    figure = section.find_all('figure')
    wallids= [wallpaper['data-wallpaper-id'] for wallpaper in figure]
    for i in wallids:
        picture = {'wallpaperid': i, 'download_link': await getdownload_url(i)}
        if (picture['download_link'] != 'null'):
            name = os.path.basename(picture['download_link'])
            picture['name'] = name
            picture['tag'] = name.split('.')[-1]
            picture['abspath'] = path + '/' + name
            picture['storagepath'] = '/image/' + datetime.now().strftime('%Y%m%d') + '/' + name
            await sqlinsert(animetype, picture)


async def download(abspath, downurl):
    with open(abspath, 'wb') as f:
        f.write(requests.get(downurl).content)


async def getdownload_url(wallid):
    try:
        downloadhtml = await openurl('https://alpha.wallhaven.cc/wallpaper/{wallid}'.format(wallid=wallid))
        html = BeautifulSoup(downloadhtml, 'lxml')
        download_url = 'https:' + html.find_all(id="wallpaper")[0]['src']
    except:
        download_url = 'null'
    return download_url


async def sqlinsert(animetype, content):
    db = pymysql.connect("localhost", "", "", "")
    cursor = db.cursor()
    table = 'animepc'
    insertsql = """INSERT INTO {table}(wallpaperid, name, tag, abspath, create_time, storagepath)
        VALUES ('{wallpaperid}', '{name}', '{tag}', '{abspath}', '{create_time}', '{storagepath}')""".format(
            table=table,
            wallpaperid=content['wallpaperid'], name=content['name'], tag=content['tag'],
            abspath=content['abspath'],create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            storagepath=content['storagepath']
        )
    selectsql = """SELECT * FROM {table} WHERE wallpaperid={id}""".format(table=table, id=content['wallpaperid'])

    cursor.execute(selectsql)
    if not cursor.fetchall():
        await download(content['abspath'], content['download_link'])
        logger.info("Success: {content} ".format(content=content))
        cursor.execute(insertsql)
        db.commit()
    else:
        logger.error("Failed: File exist. Return: {content} ".format(content=content))
        
    db.close()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.INFO)
    handler = logging.FileHandler("/var/log/script/alphasync.log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(process)d - %(thread)d - %(filename)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    path = '/var/www/image/' + datetime.now().strftime('%Y%m%d')
    if not os.path.exists(path):
        os.mkdir(path)
    alphapc = 'https://alpha.wallhaven.cc/search?q=id%3A1&categories=111&purity=100&ratios=16x10%2C16x9&sorting=relevance&order=desc&page=1'
    alphaphone = 'https://alpha.wallhaven.cc/search?q=id%3A1&categories=111&purity=100&ratios=9x16%2C10x16&sorting=relevance&order=desc&page=1'
    loop = asyncio.get_event_loop()
    tasks = [getfirstpage(alphapc, path, 'pc'), getfirstpage(alphaphone, path, 'phone')]
    loop.run_until_complete(asyncio.wait(tasks))
