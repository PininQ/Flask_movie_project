# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import admin
from flask import render_template, redirect, url_for


# 调用蓝图(app/admin/views.py)
@admin.route("/")
def index():
    return "<h1 style='color:red'>this is admin</h1>"


# 后台登录
@admin.route("/login/")
def login():
    return render_template('admin/login.html')


# 退出登录
@admin.route("/logout/")
def logout():
    return redirect(url_for('admin.login'))
