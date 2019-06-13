from info import constants
from info.models import User, News, Category
from info.modules.index import index_blu
from flask import render_template, send_file, redirect, current_app, session, request, jsonify

from info.utils.response_code import RET


@index_blu.route("/news_list")
def get_news_list():
    """
    首页新闻列表
    1、接收参数 cid page per_page
    2、校验参数合法性
    3、查询出的新闻（要关系分类）（创建时间的排序）
    4、返回响应，返回新闻数据
    :return:
    """

    cid = request.arg.get("cid")
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    # 2、校验参数合法性
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page,
                                                                                                         False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    news_list = paginate.items  # [obj, obj, obj]
    current_page = paginate.page  # 当前页
    total_page = paginate.pages  # 页数总和

    new_dict_li = []
    for news in news_list:
        new_dict_li.append(news.to_basic_dict())

    data = {
        "news_dict_li": new_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }
    return jsonify(errno=RET.OK, errmsg="OK", data=data)


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
