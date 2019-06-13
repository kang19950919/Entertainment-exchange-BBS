from flask import g, redirect, render_template

from info.utils.common import user_login
from . import profile_blu


@profile_blu.route("/info")
@user_login
def user_info():

    user = g.user
    if user:
        return redirect("/")

    data = {
        "user": user.to_dict()
    }

    return render_template("news/../../static/news/html/../../templates/news/user.html")
