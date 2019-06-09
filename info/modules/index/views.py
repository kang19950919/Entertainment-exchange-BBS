from info import constants
from info.models import User, News, Category
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
            current_app.logger.error(e)

    # 1.显示新闻排行
    click_news = []
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = [news_obj.to_basic_dict() for news_obj in click_news]

    # 2.显示首页新闻分类
    category_list = []
    try:
        category_list = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    category_list_dict = [category_obj.to_dict() for category_obj in category_list]

    data = {
        "user_info": user.to_dict() if user else None,
        "click_news_list": click_news_list,
        "category_list": category_list_dict
    }
    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    # 绝对路径，不太好
    # return send_file("E:/git_flask/BBS/Entertainment-exchange-BBS/info/static/news/favicon.ico")
    # 重定向，不太好
    # return redirect("/static/news/favicon.ico")
    return current_app.send_static_file("news/favicon.ico")