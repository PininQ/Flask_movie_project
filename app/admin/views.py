# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm
from app.models import Admin
from functools import wraps


def admin_login_req(f):
    """登录装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 调用蓝图(app/admin/views.py)
@admin.route("/")
@admin_login_req
def index():
    """首页系统管理"""
    return render_template('admin/index.html')


@admin.route("/login/", methods=["GET", "POST"])
def login():
    """后台登录"""
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['account']).first()
        # 密码错误时，check_pwd返回False,否则返回True
        if not admin.check_pwd(data['pwd']):
            flash("密码错误！")
            return redirect(url_for('admin.login'))
        # 定义session保存会话
        session['admin'] = data['account']
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('admin/login.html', form=form)


@admin.route("/logout/")
@admin_login_req
def logout():
    """退出登录"""
    session.pop('admin', None)
    return redirect(url_for('admin.login'))


@admin.route("/pwd/")
@admin_login_req
def pwd():
    """修改密码"""
    return render_template('admin/pwd.html')


@admin.route("/tag/add/")
@admin_login_req
def tag_add():
    """编辑标签"""
    return render_template('admin/tag_add.html')


@admin.route("/tag/list/")
@admin_login_req
def tag_list():
    """标签列表"""
    return render_template('admin/tag_list.html')


@admin.route("/movie/add/")
@admin_login_req
def movie_add():
    """编辑电影"""
    return render_template('admin/movie_add.html')


@admin.route("/movie/list/")
@admin_login_req
def movie_list():
    """电影列表"""
    return render_template('admin/movie_list.html')


@admin.route("/preview/add/")
@admin_login_req
def preview_add():
    """添加上映预告"""
    return render_template('admin/preview_add.html')


@admin.route("/preview/list/")
@admin_login_req
def preview_list():
    """上映预告列表"""
    return render_template('admin/preview_list.html')


@admin.route("/user/list/")
@admin_login_req
def user_list():
    """会员列表"""
    return render_template('admin/user_list.html')


@admin.route("/user/view/")
@admin_login_req
def user_view():
    """查看会员"""
    return render_template('admin/user_view.html')


@admin.route("/comment/list/")
@admin_login_req
def comment_list():
    """评论列表"""
    return render_template('admin/comment_list.html')


@admin.route("/moviecol/list/")
@admin_login_req
def moviecol_list():
    """电影收藏"""
    return render_template('admin/moviecol_list.html')


@admin.route("/oplog/list/")
@admin_login_req
def oplog_list():
    """操作日志管理"""
    return render_template('admin/oplog_list.html')


@admin.route("/adminloginlog/list/")
@admin_login_req
def adminloginlog_list():
    """管理员登录日志列表"""
    return render_template('admin/adminloginlog_list.html')


@admin.route("/userloginlog/list/")
@admin_login_req
def userloginlog_list():
    """会员登录日志列表"""
    return render_template('admin/userloginlog_list.html')


@admin.route("/auth/add/")
@admin_login_req
def auth_add():
    """添加权限"""
    return render_template("admin/auth_add.html")


@admin.route("/auth/list/")
@admin_login_req
def auth_list():
    """权限列表"""
    return render_template("admin/auth_list.html")


@admin.route("/role/add/")
@admin_login_req
def role_add():
    """添加角色"""
    return render_template("admin/role_add.html")


@admin.route("/role/list/")
@admin_login_req
def role_list():
    """角色列表"""
    return render_template("admin/role_list.html")


@admin.route("/admin/add/")
@admin_login_req
def admin_add():
    """添加管理员"""
    return render_template("admin/admin_add.html")


@admin.route("/admin/list/")
@admin_login_req
def admin_list():
    """管理员列表"""
    return render_template("admin/admin_list.html")
