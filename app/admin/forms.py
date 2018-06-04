# -*- coding: utf-8 -*-
__author__ = 'QB'

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag, Auth, Role


class LoginForm(FlaskForm):
    """管理员登录表单"""
    account = StringField(
        label="账号",
        validators=[
            DataRequired("账号不能为空！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "账号",
            # "required": "required"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "密码",
            # "required": "required"
        }
    )
    submit = SubmitField(
        "登录",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError('账号不存在！')


class TagForm(FlaskForm):
    """标签管理"""
    name = StringField(
        label="标签名称",
        validators=[
            DataRequired("标签名称不能为空！")
        ],
        description="标签",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称"
        }
    )
    submit = SubmitField(
        "添加",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class MovieForm(FlaskForm):
    """电影管理"""
    title = StringField(
        label="片名",
        validators=[
            DataRequired("片名不能为空！")
        ],
        description="片名",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片名"
        }
    )
    url = FileField(
        label="文件",
        validators=[
            DataRequired("请上传文件！")
        ],
        description="文件"
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("简介不能为空！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "style": "resize:none;",
            "rows": 10
        }
    )
    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面！")
        ],
        description="封面"
    )
    star = SelectField(
        label="星级",
        validators=[
            DataRequired("请选择星级！")
        ],
        # star的数据类型
        coerce=int,
        choices=[(1, '1星'), (2, '2星'), (3, '3星'), (4, '4星'), (5, '5星')],
        description="星级",
        render_kw={
            "class": "form-control",
        }
    )
    # 标签选择数据库中已存在的标签
    tag_id = SelectField(
        label="标签",
        validators=[
            DataRequired("请选择标签！")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in Tag.query.all()],
        description="标签",
        render_kw={
            "class": "form-control",
        }
    )
    area = StringField(
        label="上映地区",
        validators=[
            DataRequired("上映地区不能为空！")
        ],
        description="上映地区",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入上映地区"
        }
    )
    length = StringField(
        label="片长",
        validators=[
            DataRequired("片长不能为空！")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片长"
        }
    )
    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("上映时间不能为空！")
        ],
        description="上映时间",
        render_kw={
            "class": "form-control",
            "placeholder": "请选择上映时间",
            "id": "input_release_time"
        }
    )
    submit = SubmitField(
        "添加",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class PreviewForm(FlaskForm):
    """预告管理"""
    title = StringField(
        label="预告标题",
        validators=[
            DataRequired("预告标题不能为空！")
        ],
        description="预告标题",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入预告标题"
        }
    )
    logo = FileField(
        label="预告封面",
        validators=[
            DataRequired("请上传预告封面！")
        ],
        description="预告封面"
    )
    submit = SubmitField(
        "添加",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class PwdForm(FlaskForm):
    """修改密码"""
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("旧密码不能为空！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码"
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("新密码不能为空！")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码"
        }
    )
    submit = SubmitField(
        "修改",
        render_kw={
            "class": "btn btn-primary",
        }
    )

    # 验证旧密码是否正确
    def validate_old_pwd(self, field):
        from flask import session
        pwd = field.data
        # 通过session获取当前管理员的用户名
        name = session['admin']
        admin = Admin.query.filter_by(
            name=name
        ).first()
        # check_pwd方法进行密码校验
        if not admin.check_pwd(pwd):
            raise ValidationError('旧密码错误！')


class AuthForm(FlaskForm):
    name = StringField(
        label="权限名称",
        validators=[
            DataRequired("权限名称不能为空！")
        ],
        description="权限名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限名称"
        }
    )
    url = StringField(
        label="权限地址",
        validators=[
            DataRequired("权限地址不能为空！")
        ],
        description="权限地址",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限地址"
        }
    )
    submit = SubmitField(
        '添加',
        render_kw={
            "class": "btn btn-primary",
        }
    )


class RoleForm(FlaskForm):
    """角色管理"""
    name = StringField(
        label="角色名称",
        validators=[
            DataRequired("角色名称不能为空！")
        ],
        description="角色名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入角色名称"
        }
    )
    # 多选框
    auths = SelectMultipleField(
        label='权限列表',
        validators=[
            DataRequired("权限列表不能为空！")
        ],
        # 动态数据填充选择栏：列表生成器
        coerce=int,
        choices=[(v.id, v.name) for v in Auth.query.all()],
        description="权限列表",
        render_kw={
            "class": "form-control"
        }
    )
    submit = SubmitField(
        '添加',
        render_kw={
            "class": "btn btn-primary",
        }
    )


class AdminForm(FlaskForm):
    """管理员管理"""
    name = StringField(
        label="管理员名称",
        validators=[
            DataRequired("管理员名称不能为空！")
        ],
        description="管理员名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员名称",
        }
    )
    pwd = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("管理员密码不能为空！")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码",
        }
    )
    repwd = PasswordField(
        label="管理员确认密码",
        validators=[
            DataRequired("管理员确认密码不能为空！"),
            EqualTo('pwd', message='两次输入密码不一致')
        ],
        description="管理员确认密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员确认密码",
        }
    )
    role_id = SelectField(
        label="所属角色",
        coerce=int,
        choices=[(v.id, v.name) for v in Role.query.all()],
        render_kw={
            "class": "btn btn-primary"
        }
    )
    submit = SubmitField(
        "添加",
        render_kw={
            "class": "btn btn-primary"
        }
    )
