# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import home
from flask import render_template, redirect, url_for, flash, session, request, Response
from app.home.forms import RegisterForm, LoginForm, UserdetailForm, PwdForm, CommentForm, SuggestForm
from app.models import User, Userlog, Preview, Tag, Movie, Comment, Moviecol, Suggest
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import db, app, rd
from functools import wraps
import urllib
import json
import uuid
import os
from datetime import datetime

# 分页个数
PAGE_COUNT = 10


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


# 登录：调用蓝图(app/home/views.py)
@home.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        users = []
        # user = User.query.filter_by(phone=data['name']).first()
        users.append(User.query.filter_by(name=data['name']).first())
        users.append(User.query.filter_by(email=data['name']).first())
        users.append(User.query.filter_by(phone=data['name']).first())
        print(users)
        # 另一种方法是先去除列表中的None，在进行判断
        for user in users:
            if user:
                if not user.check_pwd(data['pwd']):
                    # flash("密码不正确！", "err")
                    flash("登录名或登录密码不正确！", "err")
                    return redirect(url_for("home.login"))
                session["user"] = user.name
                session["user_id"] = user.id
                ip = request.remote_addr
                address = admin_address(ip)
                userlog = Userlog(
                    user_id=user.id,
                    # ip=request.remote_addr
                    ip=ip,
                    address=address,
                )
                db.session.add(userlog)
                db.session.commit()
                return redirect(url_for("home.user"))
        # flash("用户不存在，请重新输入!", "err")
        flash("登录名或登录密码不正确!", "err")
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
    # 修改会员名之后需要重新获取user.name
    if session["user"] != user.name:
        session["user"] = user.name
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
            if user.face is not None:
                # 如果有头像，删除本地的头像。保存新的头像在本地
                if os.path.exists(app.config['FC_DIR'] + user.face):
                    os.remove(app.config['FC_DIR'] + user.face)
                    print("user.face:" + app.config['FC_DIR'] + user.face)
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


# ta主页及动态
@home.route('/user/<int:id>/<int:page>/', methods=['GET'])
def user_info(id=None, page=None):
    user = User.query.get_or_404(int(id))
    if page is None:
        page = 1
    # 电影评论个数
    comment_count = Comment.query.join(
        User
    ).filter(
        User.id == user.id
    ).count()
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == user.id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('home/userinfo.html', user=user, comment_count=comment_count, page_data=page_data)


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


# 评论记录
@home.route('/comments/<int:page>/')
@user_login_req
def comments(page=None):
    if page is None:
        page = 1
    # 电影评论个数
    comment_count = Comment.query.join(
        User
    ).filter(
        User.id == session['user_id']
    ).count()
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('home/comments.html', comment_count=comment_count, page_data=page_data)


# 登录日志
@home.route('/loginlog/<int:page>/', methods=['GET'])
@user_login_req
def loginlog(page=None):
    # 登录次数
    loginlog_count = Userlog.query.join(
        User
    ).filter(
        User.id == session['user_id']
    ).count()
    if page is None:
        page = 1
    page_data = Userlog.query.filter_by(
        user_id=int(session["user_id"])
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('home/loginlog.html', loginlog_count=loginlog_count, page_data=page_data)


# 添加电影收藏
@home.route("/moviecol/add/", methods=["GET"])
@user_login_req
def moviecol_add():
    uid = request.args.get("uid", "")
    mid = request.args.get("mid", "")
    moviecol = Moviecol.query.filter_by(
        user_id=int(uid),
        movie_id=int(mid),
    ).count()
    # 已经收藏
    if moviecol == 1:
        data = dict(ok=0)
    # 未收藏
    if moviecol == 0:
        moviecol = Moviecol(
            user_id=int(uid),
            movie_id=int(mid),
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)
    return json.dumps(data)


# 电影收藏
@home.route('/moviecol/<int:page>')
@user_login_req
def moviecol(page=None):
    if page is None:
        page = 1
    # 电影收藏个数
    moviecol_count = Moviecol.query.join(
        User
    ).filter(
        User.id == session['user_id']
    ).count()
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == session['user_id']
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    return render_template('home/moviecol.html', moviecol_count=moviecol_count, page_data=page_data)


# 网站建议
@home.route('/suggest/', methods=['GET', 'POST'])
@user_login_req
def suggest_add():
    form = SuggestForm()
    if form.validate_on_submit():
        data = form.data
        suggest = Suggest(
            user_id=session['user_id'],
            title=data['title'],
            content=data['content']
        )
        db.session.add(suggest)
        db.session.commit()
        flash("网站建议提交成功，非常感谢您提出的建议！", "ok")
        return redirect(url_for("home.suggest_add"))
    return render_template('home/suggest.html', form=form)


# 首页电影列表
@home.route('/<int:page>/', methods=['GET'])
def index(page=None):
    # 电影个数
    movie_count = Movie.query.count()
    tags = Tag.query.all()
    page_data = Movie.query
    # 标签
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    # 星级
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    # 时间
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    # 播放量
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )
    # 评论量
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=4)
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )
    return render_template('home/index.html', movie_count=movie_count, tags=tags, p=p, page_data=page_data)


@home.route('/')
def index_home():
    return redirect(url_for('home.index', page=1))


# 首页上映预告：轮播动画
@home.route('/animation/')
def animation():
    data = Preview.query.all()
    return render_template('home/animation.html', data=data)


# 电影搜索
@home.route('/search/<int:page>/')
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    # 相关电影个数
    movie_count = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    page_data.key = key
    return render_template('home/search.html', movie_count=movie_count, key=key, page_data=page_data)


# 电影详情，播放电影
@home.route('/play/<int:id>/<int:page>/', methods=['GET', 'POST'])
def play(id=None, page=None):
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)
    form = CommentForm()
    # 判断是否已经登录
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data['content'],
            movie_id=movie.id,
            user_id=session['user_id'],
        )
        db.session.add(comment)
        db.session.commit()
        commentnum = Comment.query.join(
            Movie
        ).join(
            User
        ).filter(
            Movie.id == movie.id,
            User.id == Comment.user_id
        ).count()
        movie.commentnum = commentnum
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功！", "ok")
        return redirect(url_for("home.play", id=movie.id, page=1))
    # 放在这里避免添加评论播放量+2
    movie.playnum = movie.playnum + 1
    db.session.add(movie)
    db.session.commit()
    return render_template('home/play.html', movie=movie, form=form, page_data=page_data)


# 弹幕播放器
@home.route("/video/<int:id>/<int:page>/", methods=["GET", "POST"])
def video(id=None, page=None):
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=PAGE_COUNT)

    form = CommentForm()
    # 判断是否已经登录
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data['content'],
            movie_id=movie.id,
            user_id=session['user_id'],
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功！", "ok")
        return redirect(url_for("home.video", id=movie.id, page=1))
    movie.playnum = movie.playnum + 1
    db.session.add(movie)
    db.session.commit()
    return render_template("home/video.html", movie=movie, form=form, page_data=page_data)


# 弹幕消息处理
@home.route("/tm/", methods=["GET", "POST"])
def tm():
    if request.method == "GET":
        # 获取弹幕消息队列
        id = request.args.get('id')
        # 存放在redis队列中的键值
        key = "movie" + str(id)
        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 1,
                "danmaku": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code": 1,
                "danmaku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        # 添加弹幕
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data['type'],
            "ip": request.remote_addr,
            "_id": datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player": [
                data["player"]
            ]
        }
        res = {
            "code": 1,
            "data": msg
        }
        resp = json.dumps(res)
        # 将添加的弹幕推入redis的队列中
        rd.lpush("movie" + str(data["player"]), json.dumps(msg))
    return Response(resp, mimetype='application/json')


# 额外的链接
@home.route("/sayLove2JingGe/", methods=["GET"])
def sayLove2JingGe():
    return render_template('home/sayLove2JingGe.html')


@home.route("/bl/", methods=["GET"])
def sayLove2Qiuqiu():
    return render_template('home/sayLove2Qiuqiu.html')
