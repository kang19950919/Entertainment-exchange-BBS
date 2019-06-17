from flask import Blueprint

admin_blu = Blueprint("admin", __name__, url_prefix="/admin")

from .views import *


@admin_blu.before_request
def admin_identification():
    # 先从session获取is_admin 如果能获取到 说明是管理员
    # 如果访问的是/admin/login
    is_login = request.url.endswith("/login")
    is_admin = session.get("is_admin")

    if not is_admin and not is_login:
        return redirect("/")
