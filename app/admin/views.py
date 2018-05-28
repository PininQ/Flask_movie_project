# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

# 分页个数
PAGE_COUNT = 3


def admin_login_req(f):
    """登录装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def change_filename(filename):
    """修改文件名称"""
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


def admin_page(model_name):
    count_1 = model_name.query.count()
    # 假如删除当前页是最后一页
    pre_page = int(request.args.get('pre_page')) - 1
    # 此处考虑全删完了，没法前挪的情况，0被视为false
    if not pre_page:
        pre_page = 1
    elif (count_1 - 1) % PAGE_COUNT != 0 or pre_page + 1 < count_1 / PAGE_COUNT:
        pre_page = int(request.args.get('pre_page'))
    return pre_page


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
            flash("密码错误！", 'err')
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


@admin.route("/pwd/", methods=['GET', 'POST'])
@admin_login_req
def pwd():
    """修改密码"""
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session['admin']).first()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data['new_pwd'])
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for('admin.logout'))
    return render_template('admin/pwd.html', form=form)


@admin.route("/tag/add/", methods=['GET', 'POST'])
@admin_login_req
def tag_add():
    """标签添加"""
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        # 已存在该标签
        if tag_count == 1:
            flash("标签已经存在！", "err")
            return redirect(url_for('admin.tag_add'))
        tag = Tag(
            name=data['name']
        )
        db.session.add(tag)
        db.session.commit()
        flash("标签添加成功！", "ok")
        redirect(url_for('admin.tag_add'))
    return render_template('admin/tag_add.html', form=form)


@admin.route("/tag/edit/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def tag_edit(id=None):
    """标签编辑"""
    form = TagForm()
    form.submit.label.text = "编辑"
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        if tag.name != data["name"] and tag_count == 1:
            flash("标签已经存在！", "err")
            return redirect(url_for('admin.tag_edit', id=tag.id))
        tag.name = data['name']
        db.session.add(tag)
        db.session.commit()
        flash("标签【%s】修改成功！" % tag.name, "ok")
        redirect(url_for('admin.tag_edit', id=tag.id))
    return render_template('admin/tag_edit.html', form=form, tag=tag)


@admin.route("/tag/list/<int:page>", methods=['GET'])
@admin_login_req
def tag_list(page=None):
    """标签列表"""
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/tag_list.html', page_data=page_data)


@admin.route("/tag/del/<int:id>", methods=['GET'])
@admin_login_req
def tag_del(id=None):
    """标签删除"""
    pre_page = admin_page(Tag)
    # filter_by在查不到或多个的时候并不会报错，get会报错。
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签【%s】删除成功！" % tag.name, "ok")
    return redirect(url_for('admin.tag_list', page=pre_page))


@admin.route("/movie/add/", methods=['GET', 'POST'])
@admin_login_req
def movie_add():
    """添加电影"""
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            # 创建一个多级目录
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        # url,logo为上传视频,图片之后得到的地址
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        # 保存url和logo
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        # 已存在该上映预告
        if movie_count == 1:
            flash("电影名称已经存在！", "err")
            return redirect(url_for('admin.movie_add'))
        movie = Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            star=int(data['star']),
            playnum=0,
            commentnum=0,
            tag_id=(data['tag_id']),
            area=data['area'],
            release_time=data['release_time'],
            length=data['length'],
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功！", "ok")
        return redirect(url_for('admin.movie_add'))
    return render_template('admin/movie_add.html', form=form)


@admin.route("/movie/list/<int:page>", methods=['GET'])
@admin_login_req
def movie_list(page=None):
    """电影列表"""
    if page is None:
        page = 1
    # 关联Tag的查询,单表查询使用filter_by 多表查询使用filter进行关联字段
    page_data = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/movie_list.html', page_data=page_data)


@admin.route("/movie/del/<int:id>", methods=['GET'])
@admin_login_req
def movie_del(id=None):
    """电影删除"""
    pre_page = admin_page(Movie)
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("删除电影成功！", "ok")
    return redirect(url_for('admin.movie_list', page=pre_page))


@admin.route("/movie/edit/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def movie_edit(id=None):
    """电影编辑"""
    form = MovieForm()
    form.submit.label.text = "编辑"
    # 编辑状态，url和logo已经存在，表单不必进行过滤
    form.url.validators = []
    form.logo.validators = []
    movie = Movie.query.get_or_404(int(id))
    if request.method == 'GET':
        form.info.data = movie.info
        form.star.data = movie.star
        form.tag_id.data = movie.tag_id
    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data['title']).count()
        # 片名已经存在，不必重复进行编辑
        if movie_count == 1 and movie.title != data['title']:
            flash("片名已经存在！", "err")
            return redirect(url_for('admin.movie_edit', id=id))

        # 如果目录不存在，再创建一个多级目录
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 'rw')

        # 上传视频
        if form.url.data != '':  # 说明已经重新上传了视频
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)

        # 上传logo
        if form.logo.data != '':  # 说明已经重新上传了封面
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)

        movie.title = data['title']
        movie.info = data['info']
        movie.star = data['star']
        movie.tag_id = data['tag_id']
        movie.area = data['area']
        movie.length = data['length']
        movie.release_time = data['release_time']
        db.session.add(movie)
        db.session.commit()
        flash("修改电影成功！", "ok")
        return redirect(url_for('admin.movie_edit', id=id))
    return render_template('admin/movie_edit.html', form=form, movie=movie)


@admin.route("/preview/add/", methods=['GET', 'POST'])
@admin_login_req
def preview_add():
    """添加上映预告"""
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        # 保存上映预告封面
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        logo = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logo)

        preview_count = Preview.query.filter_by(title=data["title"]).count()
        if preview_count == 1:
            flash("上映预告已经存在！", "err")
            return redirect(url_for('admin.preview_add'))
        preview = Preview(
            title=data['title'],
            logo=logo
        )
        db.session.add(preview)
        db.session.commit()
        flash("上映预告添加成功！", "ok")
        return redirect(url_for('admin.preview_add'))
    return render_template('admin/preview_add.html', form=form)


@admin.route("/preview/list/<int:page>", methods=['GET'])
@admin_login_req
def preview_list(page=None):
    """上映预告列表"""
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/preview_list.html', page_data=page_data)


@admin.route("/preview/del/<int:id>", methods=['GET'])
@admin_login_req
def preview_del(id=None):
    """上映预告删除"""
    pre_page = admin_page(Preview)
    preview = Preview.query.get_or_404(int(id))
    db.session.delete(preview)
    db.session.commit()
    flash("删除上映预告成功！", 'ok')
    return redirect(url_for('admin.preview_list', page=pre_page))


@admin.route("/preview/edit/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def preview_edit(id=None):
    """上映预告编辑"""
    form = PreviewForm()
    form.submit.label.text = "编辑"
    form.logo.validators = []
    preview = Preview.query.get_or_404(int(id))
    # get方法时，才给title赋初值
    if request.method == 'GET':
        form.title.data = preview.title
    if form.validate_on_submit():
        data = form.data
        preview_count = Preview.query.filter_by(title=data["title"]).count()
        if preview.title != data["title"] and preview_count == 1:
            flash("预告名称已经存在！", "err")
            return redirect(url_for('admin.preview_edit', id=preview.id))

        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')
        if form.logo.data != '':
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + preview.logo)

        preview.title = data['title']
        db.session.add(preview)
        db.session.commit()
        flash("上映预告【%s】修改成功！" % preview.title, "ok")
        redirect(url_for('admin.preview_edit', id=preview.id))
    return render_template('admin/preview_edit.html', form=form, preview=preview)


@admin.route("/user/list/<int:page>", methods=['GET'])
@admin_login_req
def user_list(page=None):
    """会员列表"""
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/user_list.html', page_data=page_data)


@admin.route("/user/view/<int:id>", methods=['GET'])
@admin_login_req
def user_view(id=None):
    """查看会员"""
    pre_page = request.args.get('pre_page')
    # 兼容不加参数的无来源页面访问。
    if not pre_page:
        pre_page = 1
    user = User.query.get_or_404(int(id))
    # 通过form_page参数实现返回原来的page
    return render_template('admin/user_view.html', user=user, pre_page=pre_page)


@admin.route("/user/del/<int:id>", methods=['GET'])
@admin_login_req
def user_del(id=None):
    """会员删除"""
    pre_page = admin_page(User)
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("删除会员成功！", 'ok')
    return redirect(url_for('admin.user_list', page=pre_page))


@admin.route("/comment/list/<int:page>", methods=['GET'])
@admin_login_req
def comment_list(page=None):
    """评论列表"""
    if page is None:
        page = 1
    # 通过join关联movie和user，然后过滤movie_id和user_id
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/comment_list.html', page_data=page_data)


@admin.route("/comment/del/<int:id>", methods=['GET'])
@admin_login_req
def comment_del(id=None):
    """删除评论"""
    pre_page = admin_page(Comment)
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功！", 'ok')
    return redirect(url_for('admin.comment_list', page=pre_page))


@admin.route("/moviecol/list/<int:page>", methods=['GET'])
@admin_login_req
def moviecol_list(page=None):
    """电影收藏列表"""
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/moviecol_list.html', page_data=page_data)


@admin.route("/moviecol/del/<int:id>", methods=['GET'])
@admin_login_req
def moviecol_del(id=None):
    """删除电影收藏"""
    pre_page = admin_page(Moviecol)
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除电影收藏成功！", 'ok')
    return redirect(url_for('admin.moviecol_list', page=pre_page))


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
