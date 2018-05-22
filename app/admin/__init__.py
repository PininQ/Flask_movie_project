# -*- coding: utf-8 -*-
__author__ = 'QB'
# 定义蓝图(app/admin/__init__.py)
from flask import Blueprint

admin = Blueprint("admin", __name__)

import app.admin.views
