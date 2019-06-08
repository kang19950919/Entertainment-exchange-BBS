from info.modules.index import index_blu
from flask import render_template, send_file, redirect, current_app


@index_blu.route("/")
def index():
    return render_template("news/index.html")


@index_blu.route("/favicon.ico")
def favicon():
    # return send_file("E:/git_flask/BBS/Entertainment-exchange-BBS/info/static/news/favicon.ico")
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")