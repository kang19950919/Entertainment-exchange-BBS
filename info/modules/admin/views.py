import datetime

from flask import render_template, request, current_app, session, redirect, url_for, g, jsonify, abort

from info import constants, db
from info.libs.image_storage import storage
from info.models import User, News, Category
from info.modules import Paginate
from utils.common import admin_login
from info.modules.admin import admin_blu
from utils.response_code import RET


@admin_blu.route("/news_type", methods=["GET", "POST"])
def news_type():
    """新闻分类"""
    if request.method == "GET":
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_type.html', errmsg="查询数据错误")

        category_dict_li = []
        for category in categories:
            # 取到分类的字典
            cate_dict = category.to_dict()
            category_dict_li.append(cate_dict)

        # 移除最新的分类
        category_dict_li.pop(0)

        data = {
            "categories": category_dict_li
        }

        return render_template('admin/news_type.html', data=data)
    else:
        # 1. 取参数
        c_name = request.json.get("name")
        # 如果传了cid，代表是编辑已存在的分类
        cid = request.json.get("id")

        if not c_name and not cid:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        if cid and c_name:
            # 编辑新闻分类操作
            # 有 分类 id 代表查询相关数据
            try:
                cid = int(cid)
                category = Category.query.get(cid)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

            if not category:
                return jsonify(errno=RET.NODATA, errmsg="未查询到分类数据")
            category.name = c_name
        elif not cid and c_name:
            # 增加一条分类
            category = Category()
            category.name = c_name
            db.session.add(category)
        else:
            # 删除一条分类
            try:
                cid = int(cid)
                category = Category.query.get(cid)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
            if not category:
                return jsonify(errno=RET.NODATA, errmsg="未查询到分类数据")
            db.session.delete(category)

        return jsonify(errno=RET.OK, errmsg="OK")


@admin_blu.route("/news_edit_detail", methods=["GET", "POST"])
def news_edit_detail():
    """新闻编辑详情"""
    if request.method == "GET":
        news_id = request.args.get("news_id")

        if not news_id:
            abort(404)
        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", errmsg="参数错误")

        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html", errmsg="数据查询错误")
        if not news:
            return render_template('admin/news_edit_detail.html', errmsg="未查询到数据")

        # 查询分类数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_edit_detail.html', errmsg="查询数据错误")

        categories_dict_li = []
        for category in categories:
            # 取到分类字典
            cate_dict = category.to_dict()
            # 判断当前遍历到的分类是否是当前新闻的分类，如果是，则添加is_selected为true
            # 如果当前遍历出来的分类的id 和 该条新闻的分类id一样，那么is_selected = True
            if category.id == news.category_id:
                cate_dict["is_selected"] = True
            categories_dict_li.append(cate_dict)

        # 移除最新分类
        categories_dict_li.pop(0)

        data = {
            "news": news.to_dict(),
            "categories": categories_dict_li
        }
        return render_template("admin/news_edit_detail.html", data=data)
    else:
        # 以下是POST请求
        news_id = request.form.get("news_id")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")

        if not all([news_id, title, digest, content, index_image, category_id]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数有错误")

        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

        if not news:
            return jsonify(errno=RET.NODATA, errmsg="未查询到新闻")

        # 尝试读取图片
        if index_image:
            try:
                index_image = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

            # 将图片上传到七牛
            try:
                key = storage(index_image)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.THIRDERR, errmsg="上传失败")
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        # 设置相关数据
        news.title = title
        news.digest = digest
        news.content = content
        news.category_id = category_id

        return jsonify(errno=RET.OK, errmsg="OK")


@admin_blu.route("/news_edit")
def news_edit():
    """新闻编辑"""
    filters = [News.status == 0]
    if request.args.get("keywords", None):
        filters.append(News.title.contains(request.args.get("keywords", None)))

    news_list, current_page, total_page = Paginate.find_paginate(News.query.filter(*filters), request.args.get("p", 1),
                                                                 order=True, obj=News)
    news_dict_list = [news.to_basic_dict() for news in news_list]

    context = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_dict_list
    }
    return render_template("admin/news_edit.html", data=context)


@admin_blu.route("/news_review_action", methods=["POST"])
def news_review_action():
    # 1、接收参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2、校验参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["accept", "reject"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询到指定的新闻数据
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    if action == "accept":
        # 代表接受
        news.status = 0
    else:
        reason = request.json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入拒绝原因")
        news.status = -1
        news.reason = reason

    return jsonify(errno=RET.OK, errmsg="OK")


@admin_blu.route("/news_review_detail/<int:news_id>")
def news_review_detail(news_id):
    """新闻审核页面详情"""
    # 通过id查询新闻
    news = None  # type: News
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return render_template("admin/news_review_detail.html", data={"errmsg": "未查询到此新闻"})

    # 返回数据
    data = {"news": news.to_dict()}
    return render_template("admin/news_review_detail.html", data=data)


@admin_blu.route("/news_review")
def news_review():
    """新闻审核列表页面"""
    # 如果有关键字  添加查询条件：该条新闻中的titile包含该关键字就可以了
    # 如果没有关键字  还是用原来的条件 News.status != 0
    # 如果有不同的查询，只有条件不一样。
    filters = [News.status != 0]
    if request.args.get("keywords", None):
        filters.append(News.title.contains(request.args.get("keywords", None)))

    news_list, current_page, total_page = Paginate.find_paginate(News.query.filter(*filters), request.args.get("p", 1),
                                                                 order=True, obj=News)
    news_dict_list = [news.to_review_dict() for news in news_list]

    context = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_dict_list
    }
    return render_template("admin/news_review.html", data=context)


@admin_blu.route("/user_list")
def user_list():
    """
    所有用户列表
    :return:
    """
    page = request.args.get("page", 1)

    users, current_page, total_page = Paginate.find_paginate(User.query.filter(User.is_admin == False), page)

    user_dict_li = [user.to_admin_dict() for user in users]

    data = {
        "users": user_dict_li,
        "total_page": total_page,
        "current_page": current_page
    }
    return render_template("admin/user_list.html", data=data)


@admin_blu.route("/user_count")
def user_count():
    """
    渲染用户活跃数
    :return:
    """
    # 用户总数
    total_count = User.query.filter(User.is_admin == False).count()

    # 当前的时间
    t = datetime.datetime.now()
    # 二、当月新增数 距今一个月
    # 1、找到一个"2019-06-15"的时间对象 必须先获取一个今天的时间对象
    # datetime.datetime.now()
    # 2、制造时间字符串"2019-03-01"
    mouth_date_str = "%d-%02d-01" % (t.year, t.month)
    # 将事件字符串转时间对象
    mouth_date = datetime.datetime.strptime(mouth_date_str, "%Y-%m-%d")
    mouth_count = User.query.filter(User.is_admin == False, User.create_time > mouth_date).count()

    # 三、日新增数
    day_date_str = "%d-%02d-%02d" % (t.year, t.month, t.day)
    day_date = datetime.datetime.strptime(day_date_str, "%Y-%m-%d")
    day_count = User.query.filter(User.is_admin == False, User.create_time > day_date).count()

    # 四、用户活跃人数统计
    # ["2019-05-15", "2019-05-16", "2019-05-17", ...]
    # ["100", "200", "300", ...]
    # 1、先查询出今天的登录用户总数   何为今天？？？ 2019-06-15:0:0:0 <= last_login < 2019-06-16:0:0:0
    # 2、找2019-06-15的时间对象

    activate_date = []
    activate_count = []
    for i in range(0, 31):
        start_date = day_date - datetime.timedelta(days=i - 0)  # 2019-06-15  2019-06-14  ...
        end_date = day_date - datetime.timedelta(days=i - 1)  # 2019-06-14  2019-06-13  ...
        count = User.query.filter(User.is_admin == False,
                                  User.last_login >= start_date,
                                  User.last_login < end_date).count()
        start_date_str = start_date.strftime("%Y-%m-%d")
        activate_date.append(start_date_str)
        activate_count.append(count)

        activate_date.reverse()
        activate_count.reverse()

    data = {
        "total_count": total_count,
        "mouth_count": mouth_count,
        "day_count": day_count,
        "activate_date": activate_date,
        "activate_count": activate_count
    }

    return render_template("admin/user_count.html", data=data)


@admin_blu.route("/index")
@admin_login
def index():
    """
    首页逻辑
    :return:
    """
    data = {
        "user_info": g.admin_user.to_dict()
    }
    return render_template("admin/index.html", data=data)


@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    """
    渲染后台登录界面
    :return:
    """
    if request.method == "GET":
        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="请输入用户名和密码")

    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="用户查询失败")
    if not user:
        return render_template("admin/login.html", errmsg="用户未注册")
    if not user.check_password(password):
        return render_template("admin/login.html", errmsg="密码错误")

    session["admin_id"] = user.id
    session["is_admin"] = user.is_admin

    return redirect(url_for("admin.index"))
