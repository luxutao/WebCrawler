#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys
import time
import urllib
import asyncio

import ffmpeg
import requests

"""
python3 getm3u8.py https://www.baidu.com/index.m3u8 /home/lisi/video

需要安装ffmpeg-python包以及ffmpeg软件
"""


def get_m3u8(url):
    mucontent = requests.get(url).content.decode()
    lines = [line for line in mucontent.split('\n') if line and line[0] != '#']
    return lines


def writer_ff(savepath, filename):
    with open(savepath + 'filelist.txt', 'a') as f:
        f.write('file \'%s\'\n' % filename)


async def get_ts(ts_url, savepath, filename):
    urllib.request.urlretrieve(ts_url, savepath + filename)
    print(ts_url + ' download to ' + savepath + filename)
    writer_ff(savepath, filename)


async def main(url, savepath):
    absurl = url.replace(os.path.basename(url), '')
    files = get_m3u8(url)
    if files[0][0] == '/':
        sp = url.split('/')
        absurl = '%s//%s%s' % (sp[0], sp[2], files[0].replace(os.path.basename(files[0]), ''))
    total = len(files)
    for index, filename in enumerate(files):
        filename = os.path.basename(filename)
        index = index + 1
        rate = int(index / total * 100)
        print('{filename}  {rate} {none} {index}/{total} {percent} %'\
            .format(filename=filename, rate='❤' * rate, none=' ' * (100 - rate), 
            index=index, total=total, percent=round((index / total) * 100, 2)))
        await get_ts(absurl + filename, savepath, filename)


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 2:
        loop = asyncio.get_event_loop()
        savepath = args[2] if args[2][-1] == '/' else args[2] + '/'
        if not os.path.exists(savepath) or not os.path.isdir(savepath):
            print('No such file or directory: ' + savepath)
            exit(1)
        tasks = [main(args[1], savepath)]
        loop.run_until_complete(asyncio.wait(tasks))
        while True:
            if loop.is_running():
                time.sleep(1)
            else:
                # 不知道为什么出现了acc的编码错误问题，加上后面的就好了。
                ffmpeg.input(savepath + '/filelist.txt', format='concat', safe=0).output(savepath + 'fullvideo.mp4', c='copy', **{'absf': 'aac_adtstoasc'}).run()
                print(savepath + 'fullvideo.mp4 is concat')
                break
    else:
        print('Fail, params error, try:')
        print('python3', args[0], 'your_m3u8_url', 'your_local_dir')
    # get_m3u8('https://bilibili.com-h-bilibili.com/20190223/8039_6a310f25/1000k/hls/index.m3u8')
