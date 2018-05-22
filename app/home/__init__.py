# -*- coding: utf-8 -*-
__author__ = 'QB'
# 定义蓝图(app/home/__init__.py)
from flask import Blueprint

home = Blueprint("home", __name__)

import app.home.views
