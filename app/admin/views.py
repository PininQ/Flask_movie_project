# -*- coding: utf-8 -*-
__author__ = 'QB'
from . import admin


# 调用蓝图(app/admin/views.py)
@admin.route("/")
def index():
    return "<h1 style='color:red'>this is admin</h1>"
