# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import home


# 调用蓝图(app/home/views.py)
@home.route("/")
def index():
    return "<h1 style='color:green'>this is home</h1>"
