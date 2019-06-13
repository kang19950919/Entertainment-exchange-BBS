from flask import render_template, g, current_app, abort

from info import constants
from info.models import News
from info.utils.common import user_login
from . import news_blu


@news_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    详情页渲染
    :param news_id:
    :return:
    """
    user = g.user
    # 1、查询点击排行新闻
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(
            constants.CLICK_RANK_MAX_NEWS).all()  # [obj, obj, obj]
    except Exception as e:
        current_app.logger.error(e)

    # [obj, obj, obj] --> [{}, {}, {}, {}]
    clicks_news_list = [news.to_basic_dict() for news in clicks_news]

    # 2、显示新闻的具体信息
    # 判断新闻id是否存在
    if not news_id:
        abort(404)

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    # 判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        abort(404)

    data = {
        "user_info": user.to_dict() if user else None,
        "click_news_list": clicks_news_list,
        "news": news.to_dict()
    }
    return render_template("news/detail.html", data=data)
