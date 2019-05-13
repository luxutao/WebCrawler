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
    for filename in files:
        await get_ts(absurl + filename, savepath, filename)


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 2:
        loop = asyncio.get_event_loop()
        savepath = args[2] if args[2][-1] == '/' else args[2] + '/'
        tasks = [main(args[1], savepath)]
        loop.run_until_complete(asyncio.wait(tasks))
        while True:
            if loop.is_running():
                time.sleep(1)
            else:
                ffmpeg.input(savepath + '/filelist.txt', format='concat', safe=0).output(savepath + 'fullvideo.mp4', c='copy').run()
                print(savepath + 'fullvideo.mp4 is concat')
                break
    else:
        print('Fail, params error, try:')
        print('python3', args[0], 'your_m3u8_url', 'your_local_dir\n')
    # get_m3u8('https://bilibili.com-h-bilibili.com/20190223/8039_6a310f25/1000k/hls/index.m3u8')