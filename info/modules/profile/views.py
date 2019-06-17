from flask import render_template, g, redirect, request, jsonify, current_app

from info import db, constants
from info.libs.image_storage import storage
from info.models import Category, News
from info.modules import Paginate
from utils.common import user_login
from utils.response_code import RET
from . import profile_blu


@profile_blu.route("/user_follow")
@user_login
def user_follow():
    """关注"""
    # 获取页数
    # 取到当前登录用户
    follows, current_page, total_page = Paginate.find_paginate(g.user.followed, request.args.get("p", 1))

    user_dict_li = [follow_user.to_dict() for follow_user in follows]
    data = {
        "users": user_dict_li,
        "total_page": total_page,
        "current_page": current_page
    }
    return render_template('news/user_follow.html', data=data)


@profile_blu.route("/user_news_list")
@user_login
def user_news_list():
    """
    用户发布的新闻列表页面
    :return:
    """
    news_list, current_page, total_page = Paginate.find_paginate(g.user.news_list, request.args.get("page"))

    news_dict_li = [news.to_review_dict() for news in news_list]

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("news/user_news_list.html", data=data)


@profile_blu.route("/user_news_release", methods=["GET", "POST"])
@user_login
def user_news_release():
    """
    发布新闻
    :return:
    """
    user = g.user
    if request.method == "GET":
        # 新闻分类
        category_s = Category.query.all()

        category_dict_li = [category.to_dict() for category in category_s]

        category_dict_li.pop(0)

        data = {
            "category_dict_li": category_dict_li
        }
        return render_template("news/user_news_release.html", data=data)
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        category_id = int(category_id)
        image_data = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型不正确")

    try:
        key = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="第三方上传失败")

    # 执行业务逻辑
    news = News()
    news.title = title
    news.source = "个人发布"
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = user.id
    news.status = 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")


@profile_blu.route("/user_collection")
@user_login
def user_collection():
    """
    显示用户收藏的新闻
    :return:
    """

    news_list, current_page, total_page = Paginate.find_paginate(g.user.collection_news, request.args.get("page"))

    news_dict_li = [news.to_dict() for news in news_list]

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("news/user_collection.html", data=data)


@profile_blu.route("/user_pass_info", methods=["GET", "POST"])
@user_login
def user_pass_info():
    """
    密码修改页面渲染
    :return:
    """
    user = g.user
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not user.check_password(old_password):
        return jsonify(errno=RET.PARAMERR, errmsg="密码错误")

    user.password = new_password

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="修改成功")


@profile_blu.route("/user_pic_info", methods=["GET", "POST"])
@user_login
def user_pic_info():
    """
    用户头像信息
    :return:
    """
    user = g.user
    if request.method == "GET":
        data = {
            "user_info": user.to_dict()
        }
        return render_template("news/user_pic_info.html", data=data)

    try:
        image_data = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 将用户头像上传到七牛云上
    try:
        key = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    user.avatar_url = key

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")
    return jsonify(errno=RET.OK, errmsg="上传成功", data=constants.QINIU_DOMIN_PREFIX + key)


@profile_blu.route("/user_base_info", methods=["GET", "POST"])
@user_login
def user_base_info():
    """
    用户基本信息渲染
    :return:
    """
    user = g.user

    if request.method == "GET":
        data = {
            "user_info": user.to_dict()
        }
        return render_template("news/user_base_info.html", data=data)
    else:
        nick_name = request.json.get("nick_name")
        signature = request.json.get("signature")
        gender = request.json.get("gender")

        if not all([nick_name, signature, gender]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        if gender not in ["MAN", "WOMEN"]:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")
        return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@profile_blu.route("/info")
@user_login
def pro_file():
    """
    渲染个人中心页面
    :return:
    """
    user = g.user
    if not user:
        return redirect("/")

    data = {
        "user": user.to_dict()
    }
    return render_template("news/user.html", data=data)
