from info.models import User, News
from info.modules.index import index_blu
from flask import render_template, send_file, redirect, current_app, session


@index_blu.route("/")
def index():
    # 需求：首页右上角实现
    # 依赖cookie
    # 第一次访问浏览器和redis数据库都没有cookie信息
    # 浏览器和数据库任何一方保存的session(cookie)消失session.get("user_id")为None
    user_id = session.get("user_id")  # 第一次为 None

    user = None
    if user_id:
        try:
            user = User().query.get(user_id)
        except Exception as e:
            current_app.logger.errot(e)

    # 显示新闻排行
    click_news = None
    click_news = News.query.order_by(News.clicks.desc()).limit(10).all()

    data = {
        "user_info": user.to_dict() if user else None
    }
    # data.user_info.avatar_url
    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    # 绝对路径，不太好
    # return send_file("E:/git_flask/BBS/Entertainment-exchange-BBS/info/static/news/favicon.ico")
    # 重定向，不太好
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")