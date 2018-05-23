# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import admin
from flask import render_template, redirect, url_for


# 调用蓝图(app/admin/views.py)
# 首页系统管理
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


# 编辑标签
@admin.route("/tag/add/")
def tag_add():
    return render_template('admin/tag_add.html')


# 标签列表
@admin.route("/tag/list/")
def tag_list():
    return render_template('admin/tag_list.html')


# 编辑电影
@admin.route("/movie/add/")
def movie_add():
    return render_template('admin/movie_add.html')


# 电影列表
@admin.route("/movie/list/")
def movie_list():
    return render_template('admin/movie_list.html')


# 添加上映预告
@admin.route("/preview/add/")
def preview_add():
    return render_template('admin/preview_add.html')


# 上映预告列表
@admin.route("/preview/list/")
def preview_list():
    return render_template('admin/preview_list.html')