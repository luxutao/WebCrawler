#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    上传本地图片到阿里云
"""


import os
import uuid
import glob
import asyncio
import subprocess

import pymysql

from datetime import datetime
from PIL import Image


def getglob():
    currentPath = os.path.dirname(os.path.realpath(__file__))
    piclist = glob.glob('{cp}/*'.format(cp=currentPath))
    funnpiclist = [pic for pic in piclist if os.path.basename(pic).split('.')[-1] in ['jpg', 'jpeg', 'png']]
    return funnpiclist


def isDirexist(date):
    command = "ssh ser \"[ ! -d '/var/www/image/{date}' ] && mkdir /var/www/image/{date}\"".format(date=date)
    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)


async def getfirst(filepath):
    picture = {}
    img = Image.open(filepath)
    w, h = img.size
    if (int(w) > int(h)):
        picture['pictype'] = 'pc'
    else:
        picture['pictype'] = 'phone'
    picture['wallpaperid'] = 0
    picture['filepath'] = filepath
    suffix = os.path.basename(filepath).split('.')[-1]
    picture['name'] = str(uuid.uuid4()) + '.' + suffix
    picture['tag'] = suffix
    picture['abspath'] = '/var/www/image/' + datetime.now().strftime('%Y%m%d') + '/' + picture['name']
    picture['storagepath'] = '/image/' + datetime.now().strftime('%Y%m%d') + '/' + picture['name']
    await sqlinsert(picture)


async def uploadfile(filepath, abspath):
    command = "scp {filepath} ser:{abspath}".format(filepath=filepath, abspath=abspath)
    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)


async def sqlinsert(content):
    db = pymysql.connect("localhost", "", "", "")
    cursor = db.cursor()
    table = 'anime_wallpaper'
    insertsql = """INSERT INTO {table}(wallpaperid, name, tag, abspath, create_time, storagepath, pictype)
        VALUES ('{wallpaperid}', '{name}', '{tag}', '{abspath}', '{create_time}', '{storagepath}', '{pictype}')""".format(
            table=table,
            wallpaperid=content['wallpaperid'], name=content['name'], tag=content['tag'],
            abspath=content['abspath'],create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            storagepath=content['storagepath'],
            pictype=content['pictype']
        )

    await uploadfile(content['filepath'], content['abspath'])
    print("Success: {content} ".format(content=content))
    cursor.execute(insertsql)
    db.commit()
        
    db.close()


if __name__ == '__main__':
    isDirexist(datetime.now().strftime('%Y%m%d'))
    loop = asyncio.get_event_loop()
    tasks = [getfirst(pic) for pic in getglob()]
    loop.run_until_complete(asyncio.wait(tasks))
