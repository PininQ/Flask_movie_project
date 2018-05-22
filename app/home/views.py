# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import home
from flask import render_template


# 调用蓝图(app/home/views.py)
@home.route("/")
def index():
    return render_template("home/index.html")
