#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    推送80s首页的内容到指定的邮箱
"""

import re
import sys
import requests
import base64
import smtplib
import datetime
import logging
import os

from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.image import MIMEImage
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("/tmp/used.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(process)d - %(thread)d - %(filename)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

url_80s = 'https://www.80s.tw'
username = ''  # 发件人邮箱地址
password = ''  # 发件人邮箱密码
to_addr = ['']  # 收件人邮箱地址
smtp_server = ''  # 邮箱服务提供商SMTP地址
content = ''


def open_file(filename):
    """读取文件"""
    with open(os.path.dirname(os.path.abspath(__file__)) + '/%s' % filename, 'r') as f:
        return f.read()


def open_url(url):
    """打开URL"""
    return requests.get(url, verify=False).content.decode().strip()


def format_addr(data):
    """格式化邮件地址"""
    name, addr = parseaddr(data)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendmail(username, password, to_addr, smtp_server, content):
    """发送邮件"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    msg = MIMEMultipart('alternative')  # 创建MIMEMultipart对象，代表的是父容器
    msg.attach(MIMEText(content, 'html', 'utf-8'))  # 在邮件正文中添加图片
    msg['From'] = format_addr('80s.tw<%s>' % username)
    msg['To'] = format_addr('A boring man<%s>' % to_addr)
    msg['Subject'] = Header('{0} 今日更新电影'.format(today), 'utf-8').encode()
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(username, password)
    if server.noop()[0] == 250:
        server.sendmail(username, to_addr, msg.as_string())
        logger.info('Success: Send Mail Success => 250')
    else:
        logger.error('Failure: Send Mail Failure <= {code}'.format(
            code=server.noop()[0]))
    server.close()


def change(str):
    """判断是否可以转换"""
    try:
        return float(str)
    except ValueError:
        return 0.0


def series(ul_object):
    """解析ul对象,获得每一个li的信息"""
    s = ''
    li_objects = ul_object.select('li')
    file_string = open_file('80s_template_single.html')
    for li_object in li_objects:
        s_dict = {}
        s_dict['img'] = 'http:' + li_object.img['src']
        s_dict['name'] = li_object.img['alt']
        s_dict['link'] = url_80s + li_object.a['href']
        _span = li_object.select('span')
        _tip = _span[-1].string.strip()
        if len(_tip) < 41:
            _tip += ' ღ ' * (41 - len(_tip))
        s_dict['tip'] = _tip
        _score = _span[1].string.strip()
        s_dict['score'] = change(_score)
        s = s + file_string.format(**s_dict)
    return s


def main(content=content):
    body_data = open_url(url_80s)
    bs_object = BeautifulSoup(body_data, 'lxml')
    ul_objects = bs_object.select('.me1')
    for title, ul_object in zip(['电影', '电视剧', '综艺', '动漫'], ul_objects):
        title = '<tr><td style="color:#e2e3e5;font-size:30px">{title}</td></tr>'.format(
            title=title)
        content += title + series(ul_object)
    sendmail(username, password, to_addr, smtp_server,
             open_file('80s_template.html').format(content=content))


if __name__ == '__main__':
    current_path = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(current_path + '/80s_template.html') or not os.path.exists(current_path + '/80s_template_single.html'):
        print('80s_template.html或80s_template_single.html文件不存在.')
        exit(1)
    main()
