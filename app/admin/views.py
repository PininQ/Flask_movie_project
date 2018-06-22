# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import admin
from flask import render_template, redirect, url_for, flash, session, request, abort
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm, AuthForm, RoleForm, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, Oplog, Adminlog, Userlog, Auth, Role, \
    Suggest
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import urllib
import json
import os
import uuid
from datetime import datetime

# 分页个数
PAGE_COUNT = 10


# 上下应用处理器
@admin.context_processor
def tpl_extra():
    data = dict(
        online_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    print("fileinfo:" + filename)
    print("fileinfo[-1]:" + fileinfo[-1])
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 登录装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 权限控制装饰器
def admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取当前登录的管理员Admin
        admin = Admin.query.join(
            Role
        ).filter(
            Role.id == Admin.role_id,
            Admin.id == session['admin_id']
        ).first()
        # 通过role获取权限字符串
        auths = admin.role.auths
        # print("字符串：%s" % auths)
        if auths != '':
            # 将存储形式为字符串的权限转换为整型列表
            auths = list(map(lambda v: int(v), auths.split(",")))
            auth_list = Auth.query.all()
            # 路由规则通过auths中的id去auths_list中进行查询
            urls = [v.url for v in auth_list for val in auths if v.id == val]
            # 当前访问的路由规则
            rule = request.url_rule
            # print(urls)
            # print(rule)
            # 判断当前请求的路由规则是否存在于urls，否则返回一个404的错误信息
            if str(rule) not in urls:
                abort(404)
        return f(*args, **kwargs)

    return decorated_function


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


# 根据API查询IP的地理位置
def admin_address(ipaddr):
    # ipaddr = json.load(urllib.request.urlopen('http://httpbin.org/ip'))['origin']
    # 组成查询ip地理位置的网址
    url = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s' % (ipaddr)
    # 访问url地址, urlobject是<type 'instance'>对象；
    urlobject = urllib.request.urlopen(url)
    urlcontent = urlobject.read()
    res = json.loads(urlcontent)
    # print(res)
    # 显示查询结果
    # ip = res['data']['ip']
    address = res['data']['country'] + res['data']['region'] + res['data']['city'] + " " + res['data']['isp']
    return address


# 首页：调用蓝图(app/admin/views.py)
@admin.route("/")
@admin_login_req
def index():
    """首页"""
    return render_template('admin/index.html')


# 后台登录
@admin.route("/login/", methods=["GET", "POST"])
def login():
    """后台登录"""
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data['account']).first()
        # 密码错误时，check_pwd返回False,否则返回True
        if not admin.check_pwd(data['pwd']):
            flash("密码不正确！", 'err')
            return redirect(url_for('admin.login'))
        # 定义session保存会话
        session['admin'] = data['account']
        session["admin_id"] = admin.id
        ip = request.remote_addr
        address = admin_address(ip)
        adminlog = Adminlog(
            admin_id=admin.id,
            # ip=request.remote_addr
            ip=ip,
            address=address,
        )
        db.session.add(adminlog)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('admin/login.html', form=form)


# 退出登录
@admin.route("/logout/")
@admin_login_req
def logout():
    """退出登录"""
    session.pop('admin', None)
    session.pop("admin_id", None)
    return redirect(url_for('admin.login'))


# 修改密码
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


# 标签添加
@admin.route("/tag/add/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def tag_add():
    """标签添加"""
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        # 已存在该标签
        if tag_count == 1:
            flash("标签已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.tag_add'))
        tag = Tag(
            name=data['name']
        )
        db.session.add(tag)
        db.session.commit()
        ip = request.remote_addr
        address = admin_address(ip)
        oplog = Oplog(
            admin_id=session['admin_id'],
            # 获取ip地址
            # ip=request.remote_addr,
            ip=ip,
            address=address,
            reason='添加一个标签《%s》' % data['name']
        )
        db.session.add(oplog)
        db.session.commit()
        flash("标签添加成功！", "ok")
        return redirect(url_for('admin.tag_add'))
    return render_template('admin/tag_add.html', form=form)


# 标签编辑
@admin.route("/tag/edit/<int:id>/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def tag_edit(id=None):
    """标签编辑"""
    form = TagForm()
    form.submit.label.text = "编辑"
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        if tag.name != data["name"] and tag_count == 1:
            flash("标签已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.tag_edit', id=tag.id))
        tag.name = data['name']
        db.session.add(tag)
        db.session.commit()
        flash("标签【%s】修改成功！" % tag.name, "ok")
        redirect(url_for('admin.tag_edit', id=tag.id))
    return render_template('admin/tag_edit.html', form=form, tag=tag)


# 标签列表
@admin.route("/tag/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def tag_list(page=None):
    """标签列表"""
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/tag_list.html', page_data=page_data)


# 标签删除
@admin.route("/tag/del/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def tag_del(id=None):
    """标签删除"""
    pre_page = admin_page(Tag)
    # filter_by在查不到或多个的时候并不会报错，get会报错。
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签【%s】删除成功！" % tag.name, "ok")
    return redirect(url_for('admin.tag_list', page=pre_page))


# 添加电影
@admin.route("/movie/add/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
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
            flash("片名已经存在，请重新编辑！", "err")
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


# 电影列表
@admin.route("/movie/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
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


# 电影删除
@admin.route("/movie/del/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def movie_del(id=None):
    """电影删除"""
    pre_page = admin_page(Movie)
    movie = Movie.query.get_or_404(int(id))
    # 删除本地的视频和封面
    if os.path.exists(app.config['UP_DIR'] + movie.url):
        os.remove(app.config['UP_DIR'] + movie.url)
    if os.path.exists(app.config['UP_DIR'] + movie.logo):
        os.remove(app.config['UP_DIR'] + movie.logo)
    db.session.delete(movie)
    db.session.commit()
    flash("删除电影成功！", "ok")
    return redirect(url_for('admin.movie_list', page=pre_page))


# 电影编辑
@admin.route("/movie/edit/<int:id>/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
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
            flash("片名已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.movie_edit', id=id))

        # 如果目录不存在，再创建一个多级目录
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 'rw')

        # 上传视频
        if form.url.data != '':  # 说明已经重新上传了视频
            # 先删除本地的视频
            if os.path.exists(app.config['UP_DIR'] + movie.url):
                os.remove(app.config['UP_DIR'] + movie.url)
                print("rm-movie.url:" + app.config['UP_DIR'] + movie.url)
            file_url = secure_filename(form.url.data.filename)
            print("file_url:"+file_url)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)
            print("save-movie.url:" + app.config['UP_DIR'] + movie.url)

        # 上传logo
        if form.logo.data != '':  # 说明已经重新上传了封面
            # 先删除本地的封面
            if os.path.exists(app.config['UP_DIR'] + movie.logo):
                os.remove(app.config['UP_DIR'] + movie.logo)
                print("rm-movie.logo:" + app.config['UP_DIR'] + movie.logo)
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


# 添加上映预告
@admin.route("/preview/add/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
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
            flash("上映预告已经存在，请重新编辑！", "err")
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


# 上映预告列表
@admin.route("/preview/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def preview_list(page=None):
    """上映预告列表"""
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/preview_list.html', page_data=page_data)


# 上映预告删除
@admin.route("/preview/del/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def preview_del(id=None):
    """上映预告删除"""
    pre_page = admin_page(Preview)
    preview = Preview.query.get_or_404(int(id))
    if os.path.exists(app.config['UP_DIR'] + preview.logo):
        # 删除文件，可使用以下两种方法。
        os.remove(app.config['UP_DIR'] + preview.logo)
        # os.unlink(my_file)
    db.session.delete(preview)
    db.session.commit()
    flash("删除上映预告成功！", 'ok')
    return redirect(url_for('admin.preview_list', page=pre_page))


# 上映预告编辑
@admin.route("/preview/edit/<int:id>/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
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
            flash("预告名称已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.preview_edit', id=preview.id))

        if not os.path.exists(app.config['UP_DIR']):
            os.makedirs(app.config['UP_DIR'])
            os.chmod(app.config['UP_DIR'], 'rw')
        if form.logo.data != '':
            # 删除旧的上映预告
            if os.path.exists(app.config['UP_DIR'] + preview.logo):
                os.remove(app.config['UP_DIR'] + preview.logo)
                print("preview.logo:" + app.config['UP_DIR'] + preview.logo)
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + preview.logo)

        preview.title = data['title']
        db.session.add(preview)
        db.session.commit()
        flash("上映预告【%s】修改成功！" % preview.title, "ok")
        redirect(url_for('admin.preview_edit', id=preview.id))
    return render_template('admin/preview_edit.html', form=form, preview=preview)


# 会员列表
@admin.route("/user/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def user_list(page=None):
    """会员列表"""
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/user_list.html', page_data=page_data)


# 查看会员
@admin.route("/user/view/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def user_view(id=None):
    """查看会员"""
    pre_page = request.args.get('pre_page')
    # 兼容不加参数的无来源页面访问。
    if not pre_page:
        pre_page = 1
    user = User.query.get_or_404(int(id))
    # 通过form_page参数实现返回原来的page
    return render_template('admin/user_view.html', user=user, pre_page=pre_page)


# 会员删除
@admin.route("/user/del/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def user_del(id=None):
    """会员删除"""
    pre_page = admin_page(User)
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("删除会员成功！", 'ok')
    return redirect(url_for('admin.user_list', page=pre_page))


# 评论列表
@admin.route("/comment/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
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


# 删除评论
@admin.route("/comment/del/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def comment_del(id=None):
    """删除评论"""
    pre_page = admin_page(Comment)
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功！", 'ok')
    return redirect(url_for('admin.comment_list', page=pre_page))


# 电影收藏列表
@admin.route("/moviecol/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
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


# 删除电影收藏
@admin.route("/moviecol/del/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def moviecol_del(id=None):
    """删除电影收藏"""
    pre_page = admin_page(Moviecol)
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除电影收藏成功！", 'ok')
    return redirect(url_for('admin.moviecol_list', page=pre_page))


# 操作日志管理
@admin.route("/oplog/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def oplog_list(page=None):
    """操作日志管理"""
    if page is None:
        page = 1
    page_data = Oplog.query.join(
        Admin
    ).filter(
        Admin.id == Oplog.admin_id
    ).order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/oplog_list.html', page_data=page_data)


# 管理员登录日志列表
# 不知道为什么这里必须在路径结尾加上/，否则出现404，索性给所有的路径的结尾都加上了/
@admin.route("/adminloginlog/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def adminloginlog_list(page=None):
    """管理员登录日志列表"""
    if page is None:
        page = 1
    page_data = Adminlog.query.join(
        Admin
    ).filter(
        Admin.id == Adminlog.admin_id
    ).order_by(
        Adminlog.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('admin/adminloginlog_list.html', page_data=page_data)


# 会员登录日志列表
@admin.route("/userloginlog/list/<int:page>/", methods=["GET"])
@admin_login_req
@admin_auth
def userloginlog_list(page=None):
    """会员登录日志列表"""
    if page is None:
        page = 1
    page_data = Userlog.query.join(
        User
    ).filter(
        User.id == Userlog.user_id,
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template("admin/userloginlog_list.html", page_data=page_data)


# 添加权限
@admin.route("/auth/add/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def auth_add():
    """添加权限"""
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        # 这么做避免在添加已存在的权限地址时发生sqlalchemy.exc.IntegrityError: (_mysql_exceptions.IntegrityError)
        name_count = Auth.query.filter_by(name=data["name"]).count()
        # 已存在该权限
        if name_count == 1:
            flash("权限名称已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.auth_add'))
        url_count = Auth.query.filter_by(url=data["url"]).count()
        if url_count == 1:
            flash("权限地址已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.auth_add'))
        auth = Auth(
            name=data['name'],
            url=data['url']
        )
        db.session.add(auth)
        db.session.commit()
        flash('添加权限成功！', 'ok')
        return redirect(url_for('admin.auth_add'))
    return render_template("admin/auth_add.html", form=form)


# 权限列表
@admin.route("/auth/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def auth_list(page=None):
    """权限列表"""
    if page is None:
        page = 1
    page_data = Auth.query.order_by(
        Auth.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template("admin/auth_list.html", page_data=page_data)


# 权限删除
@admin.route("/auth/del/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def auth_del(id=None):
    """权限删除"""
    pre_page = admin_page(Auth)
    auth = Auth.query.filter_by(id=id).first_or_404()
    db.session.delete(auth)
    db.session.commit()
    flash("权限【%s】删除成功！" % auth.name, "ok")
    return redirect(url_for('admin.auth_list', page=pre_page))


# 权限编辑
@admin.route("/auth/edit/<int:id>", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def auth_edit(id=None):
    form = AuthForm()
    form.submit.label.text = "编辑"
    auth = Auth.query.get_or_404(int(id))
    if form.validate_on_submit():
        data = form.data
        name_count = Auth.query.filter_by(name=data["name"]).count()
        if auth.name != data["name"] and name_count == 1:
            flash("权限名称已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.auth_edit', id=auth.id))
        # 这么做避免在添加已存在的权限地址时发生sqlalchemy.exc.IntegrityError: (_mysql_exceptions.IntegrityError)
        url_count = Auth.query.filter_by(url=data["url"]).count()
        if auth.url != data["url"] and url_count == 1:
            flash("权限地址已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.auth_edit', id=auth.id))
        auth.name = data['name']
        auth.url = data['url']
        db.session.add(auth)
        db.session.commit()
        flash("权限【%s】修改成功！" % auth.name, "ok")
        redirect(url_for('admin.auth_edit', id=auth.id))
    return render_template('admin/auth_edit.html', form=form, auth=auth)


# 添加角色
@admin.route("/role/add/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def role_add():
    """添加角色"""
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        name_count = Role.query.filter_by(name=data["name"]).count()
        if name_count == 1:
            flash("角色名称已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.role_add'))
        role = Role(
            name=data['name'],
            # 通过map函数将数字转换称字符串进行join
            auths=",".join(map(lambda v: str(v), data['auths']))
        )
        db.session.add(role)
        db.session.commit()
        flash('添加权限成功！', 'ok')
        return redirect(url_for('admin.role_add'))
    return render_template("admin/role_add.html", form=form)


# 角色列表
@admin.route("/role/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def role_list(page=None):
    """角色列表"""
    if page is None:
        page = 1
    page_data = Role.query.order_by(
        Role.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template("admin/role_list.html", page_data=page_data)


# 角色删除
@admin.route("/role/del/<int:id>/", methods=['GET'])
@admin_login_req
@admin_auth
def role_del(id=None):
    """角色删除"""
    pre_page = admin_page(Role)
    role = Role.query.get_or_404(int(id))
    db.session.delete(role)
    db.session.commit()
    flash("角色【%s】删除成功！" % role.name, "ok")
    return redirect(url_for('admin.role_list', page=pre_page))


# 角色编辑
@admin.route("/role/edit/<int:id>", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def role_edit(id=None):
    form = RoleForm()
    form.submit.label.text = "编辑"
    role = Role.query.get_or_404(int(id))
    # 请求方式为GET时进行赋值。多选框无法在模板中赋初值
    if request.method == 'GET':
        auths = role.auths
        # 字符串分隔成数组，转换成整型然后转换成列表
        form.auths.data = list(map(lambda v: int(v), auths.split(',')))
    if form.validate_on_submit():
        data = form.data
        name_count = Role.query.filter_by(name=data["name"]).count()
        if role.name != data["name"] and name_count == 1:
            flash("角色名称已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.role_edit', id=role.id))
        role.name = data['name']
        role.auths = ','.join(map(lambda v: str(v), data['auths']))
        db.session.add(role)
        db.session.commit()
        flash("角色【%s】修改成功！" % role.name, "ok")
        redirect(url_for('admin.role_edit', id=role.id))
    return render_template('admin/role_edit.html', form=form, role=role)


# 添加管理员
@admin.route("/admin/add/", methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def admin_add():
    """添加管理员"""
    form = AdminForm()
    from werkzeug.security import generate_password_hash
    if form.validate_on_submit():
        data = form.data
        name_count = Admin.query.filter_by(name=data["name"]).count()
        if name_count == 1:
            flash("管理员名称已经存在，请重新编辑！", "err")
            return redirect(url_for('admin.admin_add'))
        admin = Admin(
            name=data['name'],
            pwd=generate_password_hash(data['pwd']),
            role_id=data['role_id'],
            is_super=1
        )
        db.session.add(admin)
        db.session.commit()
        flash("添加管理员成功！", "ok")
    return render_template("admin/admin_add.html", form=form)


# 管理员列表
@admin.route("/admin/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def admin_list(page=None):
    """管理员列表"""
    if page is None:
        page = 1
    page_data = Admin.query.join(
        Role
    ).filter(
        Role.id == Admin.role_id
    ).order_by(
        Admin.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template("admin/admin_list.html", page_data=page_data)


# 网站建议列表
@admin.route("/suggest/list/<int:page>/", methods=['GET'])
@admin_login_req
@admin_auth
def suggest_list(page=None):
    if page is None:
        page = 1
    page_data = Suggest.query.join(
        User
    ).filter(
        User.id == Suggest.user_id
    ).order_by(
        Suggest.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template("admin/suggest_list.html", page_data=page_data)
