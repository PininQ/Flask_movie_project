# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import home
from flask import render_template, redirect, url_for


# 调用蓝图(app/home/views.py)
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


# 会员中心
@home.route('/user/')
def user():
    return render_template('home/user.html')


# 修改密码
@home.route('/pwd/')
def pwd():
    return render_template('home/pwd.html')


# 评论记录
@home.route('/comments/')
def comments():
    return render_template('home/comments.html')


# 登录日志
@home.route('/loginlog/')
def loginlog():
    return render_template('home/loginlog.html')


# 收藏电影
@home.route('/moviecol/')
def moviecol():
    return render_template('home/moviecol.html')


# 列表
@home.route('/')
def index():
    return render_template('home/index.html')


# 动画
@home.route('/animation/')
def animation():
    return render_template('home/animation.html')