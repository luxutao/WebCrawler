#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import re
import time
import html
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.image import MIMEImage

import requests
import pymysql

def open_file(filename):
    """读取文件"""
    with open(os.path.dirname(os.path.abspath(__file__)) + '/%s' % filename, 'r') as f:
        return f.read()

def format_addr(data):
    """格式化邮件地址"""
    name, addr = parseaddr(data)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def sendmail(username, password, to_addr, smtp_server, content):
    """发送邮件"""
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    msg = MIMEMultipart('alternative')  # 创建MIMEMultipart对象，代表的是父容器
    msg.attach(MIMEText(content, 'html', 'utf-8'))  # 在邮件正文中添加图片
    msg['From'] = format_addr('AK视频<%s>' % username)
    msg['Bcc'] = ','.join(to_addr)
    msg['Subject'] = Header('{0} 昨日更新电影'.format(yesterday), 'utf-8').encode()
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(username, password)
    if server.noop()[0] == 250:
        server.sendmail(username, to_addr, msg.as_string())

def getSqlData(db, sql):
    "获取数据库的数据"
    connection = pymysql.connect(host='localhost', 
        port=3306,
        user='root',
        password='123456',
        db=db,
        charset='utf8')
    cursor = connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def getTime():
    "获取昨天的时间范围"
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_start_time = int(time.mktime(time.strptime(str(yesterday), '%Y-%m-%d')))
    yesterday_end_time = int(time.mktime(time.strptime(str(today), '%Y-%m-%d'))) - 1
    return yesterday_start_time, yesterday_end_time

def getUserEmail():
    "获取已经注册的用户邮箱列表"
    blacklist = []
    # with open('/var/www/flaskapi/blacklist') as f:
    #     blacklist = f.readlines()
    emails = getSqlData('app', 'SELECT email FROM users')
    return [row[0] for row in emails if row[0] not in blacklist]

def getVideoType():
    "获取类型"
    types = getSqlData('seacms', 'SELECT tid,tname FROM sea_type')
    return {str(t[0]): t[1] for t in types}

def seriesList(listdata):
    s = ''
    html_string = open_file('ak_template_single.html')
    for data in listdata:
        s = s + html_string.format(**data)
    return s

def main():
    detail = 'http://v.animekid.cn/detail/?{v_id}.html'
    VIDEO_SQL = 'SELECT sea_data.v_id,sea_data.tid,sea_data.v_name,sea_data.v_pic,sea_data.v_score,\
        sea_content.body FROM sea_data,sea_content WHERE sea_data.v_id=sea_content.v_id AND \
        sea_data.v_addtime>%s AND sea_data.v_addtime<=%s' % getTime()
    videos = getSqlData('seacms', VIDEO_SQL)
    moveis = []; tvs = []; animes = []; shows = []
    mt = [1, 5, 6, 7, 8, 9, 10, 11, 12]
    tt = [2, 13, 14, 15, 16]; at = [4]; st = [3]
    for video in videos:
        rowdata = dict(zip(['v_id', 'tid', 'v_name', 'v_pic', 'v_score', 'body'], list(video)))
        rowdata['link'] = detail.format(v_id=rowdata['v_id'])
        rowdata['body'] = re.compile(r'<[^>]+>', re.S).sub('', html.unescape(rowdata['body'])).replace('&nbsp;', '')[:50]
        if rowdata['tid'] in mt:
            moveis.append(rowdata)
        if rowdata['tid'] in tt:
            tvs.append(rowdata)
        if rowdata['tid'] in at:
            animes.append(rowdata)
        if rowdata['tid'] in st:
            shows.append(rowdata)
    content_temp = open_file('ak_template.html')
    content = ''
    for title, object_type in zip(['电影', '电视剧', '综艺', '动漫'], [moveis, tvs, shows, animes]):
        title = '<tr><td style="color:#e2e3e5;font-size:30px">{title}</td></tr>'.format(
            title=title)
        content += title + seriesList(object_type)
    sendmail('', '', getUserEmail(), 'smtp.animekid.cn', content_temp.format(content=content))


if __name__ == "__main__":
    main()
