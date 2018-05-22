# -*- coding: utf-8 -*-
__author__ = 'QB'

from flask import Flask

app = Flask(__name__)
app.debug = True

# 注册蓝图(app/__init__.py)
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")
