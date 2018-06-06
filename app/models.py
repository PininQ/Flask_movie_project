# -*- coding: utf-8 -*-
__author__ = 'QB'

from datetime import datetime
from app import db


class User(db.Model):
    """会员数据模型"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码
    email = db.Column(db.String(100), unique=True)  # 邮箱
    phone = db.Column(db.String(11), unique=True)  # 手机号码
    info = db.Column(db.Text)  # 个性简介
    face = db.Column(db.String(255), unique=True)  # 头像
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 注册时间
    uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
    # （设置外键的第二步，指向Userlog模型，进行一个互相关系的绑定）
    userlogs = db.relationship('Userlog', backref='user')  # 会员日志外键关系关联
    comments = db.relationship('Comment', backref='user')  # 评论外键关系关联
    moviecols = db.relationship('Moviecol', backref='user')  # 电影收藏外键关系关联
    suggests = db.relationship('Suggest', backref='user')  # 网站建议外键关系关联

    def __repr__(self):
        return '<User %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


class Userlog(db.Model):
    """会员登录日志数据模型"""
    __tablename__ = 'userlog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    # （下面是设置外键的第一步）:指向user表的id字段
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
    ip = db.Column(db.String(100))  # ip地址
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间
    address = db.Column(db.String(100))  # 地址

    def __repr__(self):
        return '<Userlog %r>' % self.id


class Tag(db.Model):
    """标签数据模型"""
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 标题
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加电影时间
    # （设置外键的第二步）
    movies = db.relationship('Movie', backref='tag')  # 电影外键关系关联

    def __repr__(self):
        return '<Tag %r>' % self.name


class Movie(db.Model):
    """电影数据模型"""
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 标题
    url = db.Column(db.String(255), unique=True)  # 文件地址
    info = db.Column(db.Text)  # 电影简介
    logo = db.Column(db.String(255), unique=True)  # 封面地址
    star = db.Column(db.SmallInteger)  # 星级
    playnum = db.Column(db.BigInteger)  # 播放量
    commentnum = db.Column(db.BigInteger)  # 评论量
    # （设置外键第一步）
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # 所属标签
    area = db.Column(db.String(255))  # 上映地区
    release_time = db.Column(db.Date)  # 上映时间
    length = db.Column(db.String(100))  # 电影播放时间长度
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    comments = db.relationship('Comment', backref='movie')  # 评论外键关系关联
    moviecols = db.relationship('Moviecol', backref='movie')  # 电影收藏外键关系关联

    def __repr__(self):
        return '<Movie %r>' % self.title


class Preview(db.Model):
    """上映预告数据模型"""
    __tablename__ = 'preview'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 标题
    logo = db.Column(db.String(255), unique=True)  # 封面
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Preview %r>' % self.title


class Comment(db.Model):
    """评论数据模型"""
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)  # 评论内容
    # 关联外键第一步，还要去user表和movie表进行第二步
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Comment %r>' % self.id


class Moviecol(db.Model):
    """电影收藏数据模型"""
    __tablename__ = 'moviecol'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    # 关联外键第一步，还要去user表和movie表进行第二步
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Moviecol %r>' % self.id


class Auth(db.Model):
    """权限数据模型"""
    __tablename__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    url = db.Column(db.String(255), unique=True)  # url地址
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间

    def __repr__(self):
        return '<Auth %r>' % self.name


class Role(db.Model):
    """角色数据模型"""
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    auths = db.Column(db.String(600))  # 角色权限列表
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间
    admins = db.relationship('Admin', backref='role')  # 管理员外键关系关联

    def __repr__(self):
        return '<Role %r>' % self.name


class Admin(db.Model):
    """管理员数据模型"""
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 管理员账号
    pwd = db.Column(db.String(100))  # 管理员密码
    is_super = db.Column(db.SmallInteger)  # 是否为超级管理员，0为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 所属角色
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    adminlogs = db.relationship('Adminlog', backref='admin')  # 管理员登录日志外键关系关联
    oplogs = db.relationship('Oplog', backref='admin')  # 管理员操作日志外键关系关联

    def __repr__(self):
        return '<Admin %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


class Adminlog(db.Model):
    """管理员登录日志数据模型"""
    __tablename__ = 'adminlog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间
    address = db.Column(db.String(100))  # 地址

    def __repr__(self):
        return '<Adminlog %r>' % self.id


class Oplog(db.Model):
    """管理员操作日志数据模型"""
    __tablename__ = 'oplog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 操作IP
    reason = db.Column(db.String(600))  # 操作原因
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登录时间
    address = db.Column(db.String(100))  # 地址

    def __repr__(self):
        return '<Oplog %r>' % self.id


class Suggest(db.Model):
    """网站建议数据模型"""
    __tablename__ = 'suggest'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    # （下面是设置外键的第一步）:指向user表的id字段
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
    title = db.Column(db.String(100))  # 标题
    content = db.Column(db.String(600))  # 网站建议内容
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 提交时间

    def __repr__(self):
        return '<Suggest %r>' % self.id

# # 执行创建表语句
# if __name__ == '__main__':
#     # 删除表
#     db.drop_all()
#
#     # 创建表
#     db.create_all()
#
#     role = Role(
#         name="超级管理员",
#         auths=""
#     )
#     db.session.add(role)
#     db.session.commit()
#
#     from werkzeug.security import generate_password_hash
#
#     admin = Admin(
#         name="movie",
#         pwd=generate_password_hash("movie"),
#         is_super=0,
#         role_id=1
#     )
#     db.session.add(admin)
#     db.session.commit()
#
#     app.run(debug=True)
