# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegisterForm, LoginForm, UserdetailForm, PwdForm
from app.models import User, Userlog
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import db, app
from functools import wraps
import uuid
import os
from datetime import datetime


# 登录装饰器
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            # next页面为当前请求的url
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 登录：调用蓝图(app/home/views.py)
@home.route('/login/', methods=['GET', 'POST'])
def login():
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


# 退出
@home.route('/logout/')
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    # 重定向到home模块下的登录
    return redirect(url_for('home.login'))


# 会员注册
@home.route('/register/', methods=['GET', 'POST'])
def register():
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


# 会员中心个人资料
@home.route('/user/', methods=['GET', 'POST'])
@user_login_req
def user():
    form = UserdetailForm()
    user = User.query.get(int(session['user_id']))
    form.face.validators = []
    if request.method == 'GET':
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        if not os.path.exists(app.config['FC_DIR']):
            os.makedirs(app.config['FC_DIR'])
            os.chmod(app.config['DC_DIR'], 'rw')
        # 上传头像
        if form.face.data != '':  # 说明已经重新上传了头像
            file_face = secure_filename(form.face.data.filename)
            user.face = change_filename(file_face)
            form.face.data.save(app.config['FC_DIR'] + user.face)

        # 会员名、邮箱、手机号码有可能重复
        name_count = User.query.filter_by(name=data['name']).count()
        if data['name'] != user.name and name_count == 1:
            flash("会员名已经存在，请重新编辑", "err")
            return redirect(url_for("home.user"))

        email_count = User.query.filter_by(email=data['email']).count()
        if data['email'] != user.email and email_count == 1:
            flash("邮箱已经存在，请重新编辑", "err")
            return redirect(url_for("home.user"))

        phone_count = User.query.filter_by(phone=data['phone']).count()
        if data['phone'] != user.phone and phone_count == 1:
            flash("手机号码已经存在，请重新编辑", "err")
            return redirect(url_for("home.user"))

        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.info = data['info']
        db.session.add(user)
        db.session.commit()
        flash("修改成功！", "ok")
        return redirect(url_for("home.user"))
    return render_template('home/user.html', form=form, user=user)


# 修改密码
@home.route('/pwd/', methods=['GET', 'POST'])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=session['user']).first()
        if not user.check_pwd(data['old_pwd']):
            flash("旧密码不正确！", "err")
            return redirect(url_for("home.pwd"))
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for("home.logout"))
    return render_template('home/pwd.html', form=form)


@home.route('/comments/')
@user_login_req
def comments():
    """评论记录"""
    return render_template('home/comments.html')


# 登录日志
@home.route('/loginlog/<int:page>/', methods=['GET'])
@user_login_req
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.filter_by(
        user_id=int(session["user_id"])
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=5)
    return render_template('home/loginlog.html',page_data=page_data)


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
