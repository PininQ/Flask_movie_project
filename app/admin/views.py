# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import admin
from flask import render_template, redirect, url_for


# 调用蓝图(app/admin/views.py)
@admin.route("/")
def index():
    return render_template('admin/index.html')


# 后台登录
@admin.route("/login/")
def login():
    return render_template('admin/login.html')


# 退出登录
@admin.route("/logout/")
def logout():
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route("/pwd/")
def pwd():
    return render_template('admin/pwd.html')
