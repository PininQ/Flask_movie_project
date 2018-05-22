# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import home
from flask import render_template, redirect, url_for


# 调用蓝图(app/home/views.py)
@home.route("/")
def index():
    return render_template("home/index.html")


# 登录
@home.route('/login/')
def login():
    return render_template('home/login.html')


# 退出
@home.route('/logout/')
def logout():
    # 重定向到home模块下的登录
    return redirect(url_for('home.login'))


# 注册
@home.route('/register/')
def register():
    return render_template('home/register.html')
