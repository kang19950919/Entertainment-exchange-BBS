from flask import render_template, send_file, current_app, session, request, jsonify, g

from info import constants
from info.models import News, User, Category
from info.modules.index import index_blu
from utils.common import user_login
from utils.response_code import RET


@index_blu.route("/get_news_list")
def get_new_list():
    """
    1.接收参数 cid  page  per_page
    2.校验参数
    3.读取数据库信息
    4.返回响应
    :return:
    """

    cid = request.args.get("cid")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数不正确")

    # 因为新闻分类没有id为1的所以为1要查询所有数据
    filters = [News.status == 0]  # 0 表示通过审核了
    if cid != 1:
        filters.append(News.category_id == cid)

    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).\
            paginate(page=page, per_page=per_page, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    news_obj_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    news_dict_list = []
    for obj in news_obj_list:
        news_dict_list.append(obj.to_basic_dict())

    data = {
        "news_dict_list": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)


@index_blu.route("/")
@user_login
def index():
    # 通过session获取用的信息，底层依赖于cookie
    user = g.user

    # 1、首页点击排行
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)

    # [obj, obj, obj] --> [{}, {}, {}, {}]
    news_dict_list = [new_obj.to_dict() for new_obj in clicks_news]

    # 2、显示新闻分类
    category_s = []
    try:
        category_s = Category.query.all()  # [obj, obj]
    except Exception as e:
        current_app.logger.error(e)

    # category_s_li = []  # [{}, {}, {}]
    # for category in category_s:
    #     category_s_dict = category.to_dict()
    #     category_s_li.append(category_s_dict)
    # 使用列表表达式返回[{}, {}, {}]数据
    category_s_li = [category.to_dict() for category in category_s]

    data = {
        # 如果user不为空为user.to_dict()
        "user": user.to_dict() if user else None,
        "news_dict_list": news_dict_list,
        "category_s": category_s_li
    }

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    # 返回图标
    # return send_file()  # 需要文件的绝对路径
    return current_app.send_static_file("news/favicon.ico")
