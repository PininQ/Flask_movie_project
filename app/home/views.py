# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import home
from flask import render_template, redirect, url_for


# 调用蓝图(app/home/views.py)
@home.route('/login/')
def login():
    """登录"""
    return render_template('home/login.html')


@home.route('/logout/')
def logout():
    """退出"""
    # 重定向到home模块下的登录
    return redirect(url_for('home.login'))


@home.route('/register/')
def register():
    """注册"""
    return render_template('home/register.html')


@home.route('/user/')
def user():
    """会员中心"""
    return render_template('home/user.html')


@home.route('/pwd/')
def pwd():
    """修改密码"""
    return render_template('home/pwd.html')


@home.route('/comments/')
def comments():
    """评论记录"""
    return render_template('home/comments.html')


@home.route('/loginlog/')
def loginlog():
    """登录日志"""
    return render_template('home/loginlog.html')


@home.route('/moviecol/')
def moviecol():
    """收藏电影"""
    return render_template('home/moviecol.html')


@home.route('/')
def index():
    """首页电影列表"""
    return render_template('home/index.html')


@home.route('/animation/')
def animation():
    """首页轮播动画"""
    return render_template('home/animation.html')


@home.route('/search/')
def search():
    """电影搜索"""
    return render_template('home/search.html')


@home.route('/play/')
def play():
    """电影详情"""
    return render_template('home/play.html')
