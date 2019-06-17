from flask import Blueprint

new_blu = Blueprint("news", __name__, url_prefix="/news")

from .views import *
