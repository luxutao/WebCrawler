#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Description:
    模拟登陆拉勾
"""

import hashlib
import requests
import json
import time
import re

from bs4 import BeautifulSoup
from contextlib import closing


class LagouLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.HEADERS = {
            'Referer': 'https://passport.lagou.com/login/login.html',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/66.0.3359.139 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

    def get_token(self):
        """获得登录页面动态token和code"""
        login_url = 'https://passport.lagou.com/login/login.html'
        body = self.session.get(login_url, headers=self.HEADERS)
        lagou_soup = BeautifulSoup(
            markup=body.content, features='lxml', from_encoding='utf-8')
        x_anti = lagou_soup.find_all('script')[1].getText().split('\n')
        x_anti = [str(line).strip() for line in x_anti if line]
        token = {
            'X-Anit-Forge-Token': re.findall(r'= \'(.+?)\'', x_anti[0])[0],
            'X-Anit-Forge-Code': re.findall(r'= \'(.+?)\'', x_anti[1])[0]
        }
        return token

    def encryp_password(self):
        """加密密码"""
        password = hashlib.md5(self.password.encode('utf-8')).hexdigest()
        password = 'veenike' + password + 'veenike'
        password = hashlib.md5(password.encode('utf-8')).hexdigest()
        return password

    def login(self):
        """登陆"""
        post_data = {
            'isValidate': 'true',
            'username': self.username,
            'password': self.encryp_password(),
            'request_form_verifyCode': '',
            'submit': ''
        }
        post_url = 'https://passport.lagou.com/login/login.json'
        headers = self.HEADERS.copy()
        headers.update(self.get_token())
        response = self.session.post(
            url=post_url, data=post_data, headers=headers)
        result = json.loads(response.content.decode())

        if result.get('state') == 1:
            print(result)
            return self.session
        else:
            return None


if __name__ == '__main__':
    login = LagouLogin('', '')
    login.login()
