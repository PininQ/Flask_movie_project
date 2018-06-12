# -*- coding: utf-8 -*-
__author__ = 'QB'

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
import os

app = Flask(__name__)
# 配置数据库跟踪地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:qiu66666@127.0.0.1:3306/movie'
# 跟踪数据库的修改 --> 不建议开启 未来的版本中会移除
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["REDIS_URL"] = "redis://:qiu66666@127.0.0.1:6379/0"
app.config['SECRET_KEY'] = 'qinbin'
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), r"static\\uploads\\")
app.config['FC_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), r"static\\uploads\\users\\")
app.debug = True
db = SQLAlchemy(app)
rd = FlaskRedis(app)

# 注册蓝图(app/__init__.py)
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")


# 404页面
@app.errorhandler(404)
def page_not_found(error):
    return render_template('home/404.html'), 404
