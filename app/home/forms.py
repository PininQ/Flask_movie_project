# -*- coding: utf-8 -*-
__author__ = 'QB'

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, Regexp, EqualTo, ValidationError, Length
from app.models import User


# 注册
class RegisterForm(FlaskForm):
    name = StringField(
        label="会员名",
        validators=[
            DataRequired("会员名不能为空!"),
            Length(1, 12, "会员名不能超过12个字符")
        ],
        description="会员名",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "会员名"
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("邮箱不能为空!"),
            # Email("邮箱格式不正确！"),
            Regexp("^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$", message="邮箱格式不正确！"),
            Length(5, 50, "邮箱长度最大为50个字符")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "邮箱"
        }
    )
    phone = StringField(
        label="手机号码",
        validators=[
            DataRequired("手机号码不能为空!"),
            Regexp("^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$", message="手机号码格式不正确！")
        ],
        description="手机号码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "手机号码"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空！"),
            Length(6, 18, "密码为6-18个字符！"),
            Regexp("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,18}$", message="密码需要包含字母和数字！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "密码",
        }
    )
    repwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("确认密码不能为空！"),
            EqualTo('pwd', message='两次输入密码不一致'),
            Length(6, 18, "密码为6-18个字符！"),
            Regexp("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,18}$", message="密码需要包含字母和数字！")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "确认密码",
        }
    )
    submit = SubmitField(
        "注册",
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    def validate_name(self, field):
        name = field.data
        for v in name:
            if v == ' ' or v == '\t' or v == '\r':
                raise ValidationError("会员名不能包含空格！")
        user = User.query.filter_by(name=name).count()
        if user == 1:
            raise ValidationError("昵称已经存在！")

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError("邮箱已经存在！")

    def validate_phone(self, field):
        phone = field.data
        user = User.query.filter_by(phone=phone).count()
        if user == 1:
            raise ValidationError("手机号码已经存在！")


class LoginForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            DataRequired("账号不能为空!"),
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "会员名/邮箱/手机号码"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "密码",
        }
    )
    submit = SubmitField(
        "登录",
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )


class UserdetailForm(FlaskForm):
    name = StringField(
        label="会员名",
        validators=[
            DataRequired("会员名不能为空!"),
            Length(1, 12, "会员名不能超过12个字符")
        ],
        description="会员名",
        render_kw={
            "class": "form-control",
            "placeholder": "请设置会员名"
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("邮箱不能为空!"),
            # Email("邮箱格式不正确！"),
            Regexp("^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$", message="邮箱格式不正确！"),
            Length(5, 50, "邮箱长度最大为50个字符")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱"
        }
    )
    phone = StringField(
        label="手机号码",
        validators=[
            DataRequired("手机号码不能为空!"),
            Regexp("^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$", message="手机号码格式不正确！")
        ],
        description="手机号码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机号码"
        }
    )
    face = FileField(
        label='头像',
        validators=[
            DataRequired("请上传头像！"),
        ],
        description="头像",
        render_kw={
            "style": "margin-bottom:6px;"
        }
    )
    info = TextAreaField(
        label="简介",
        validators=[
            # DataRequired("简介不能为空！"),
            Length(max=150, message="个人简介不能超过150个字符")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入简介",
            "style": "resize:none;font-size:16px",
            "rows": 4
        }
    )
    submit = SubmitField(
        '保存修改',
        render_kw={
            "class": "btn btn-success"
        }
    )


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("旧密码不能为空！"),
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "旧密码",
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("新密码不能为空！"),
            Length(6, 18, "密码为6-18个字符！"),
            Regexp("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,18}$", message="密码需要包含字母和数字！")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "新密码",
        }
    )
    repwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("确认密码不能为空！"),
            EqualTo('new_pwd', message='两次输入密码不一致'),
            Length(6, 18, "密码为6-18个字符！"),
            Regexp("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,18}$", message="密码需要包含字母和数字！")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control",
            "placeholder": "确认密码",
        }
    )
    submit = SubmitField(
        "修改密码",
        render_kw={
            "class": "btn btn-success"
        }
    )


class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("请输入内容！"),
        ],
        description="内容",
        render_kw={
            "id": "input_content"
        }
    )
    submit = SubmitField(
        "提交评论",
        render_kw={
            "class": "btn btn-success",
            "id": "btn-sub"
        }
    )


class SuggestForm(FlaskForm):
    title = StringField(
        label="标题",
        validators=[
            DataRequired("标题不能为空!"),
        ],
        description="标题",
        render_kw={
            "class": "form-control",
            "placeholder": "标题"
        }
    )
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("内容不能为空!"),
            Length(max=500, message="内容不能超过500个字符")
        ],
        description="内容",
        render_kw={
            "class": "form-control",
            "placeholder": "内容",
            "style": "resize:none;font-size:16px",
            "rows": 10
        }
    )
    submit = SubmitField(
        "提交建议",
        render_kw={
            "class": "btn btn-success",
            "id": "btn-sub"
        }
    )
