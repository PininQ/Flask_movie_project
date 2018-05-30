# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegisterForm, LoginForm
from app.models import User, Userlog
from werkzeug.security import generate_password_hash
from app import db, app
from functools import wraps
import uuid


# 登录装饰器
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            # next页面为当前请求的url
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 登录：调用蓝图(app/home/views.py)
@home.route('/login/', methods=['GET', 'POST'])
def login():
    """登录"""
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        users = []
        users.append(User.query.filter_by(name=data['name']).first())
        users.append(User.query.filter_by(email=data['name']).first())
        users.append(User.query.filter_by(phone=data['name']).first())
        # user = User.query.filter_by(phone=data['name']).first()
        print(users)
        # 另一种方法是先去除列表中的None，在进行判断
        for user in users:
            if user:
                if not user.check_pwd(data['pwd']):
                    flash("密码不正确！", "err")
                    return redirect(url_for("home.login"))
                session["user"] = user.name
                session["user_id"] = user.id
                userlog = Userlog(
                    user_id=user.id,
                    ip=request.remote_addr
                )
                db.session.add(userlog)
                db.session.commit()
                return redirect(url_for("home.user"))
        flash("用户不存在，请重新输入!", "err")
        return redirect(url_for("home.login"))
    return render_template('home/login.html', form=form)


@home.route('/logout/')
def logout():
    """退出"""
    session.pop("user", None)
    session.pop("user_id", None)
    # 重定向到home模块下的登录
    return redirect(url_for('home.login'))


# 会员注册
@home.route('/register/', methods=['GET', 'POST'])
def register():
    """注册"""
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            pwd=generate_password_hash(data['pwd']),
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功！", "ok")
    return render_template('home/register.html', form=form)


@home.route('/user/')
@user_login_req
def user():
    """会员中心"""
    return render_template('home/user.html')


@home.route('/pwd/')
@user_login_req
def pwd():
    """修改密码"""
    return render_template('home/pwd.html')


@home.route('/comments/')
@user_login_req
def comments():
    """评论记录"""
    return render_template('home/comments.html')


@home.route('/loginlog/')
@user_login_req
def loginlog():
    """登录日志"""
    return render_template('home/loginlog.html')


@home.route('/moviecol/')
@user_login_req
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
