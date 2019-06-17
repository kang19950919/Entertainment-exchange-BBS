from flask import render_template, current_app, abort, session, g, request, jsonify

from info import constants, db
from info.models import News, User, Comment, CommentLike
from info.modules.news import new_blu
from utils.common import user_login
from utils.response_code import RET


@new_blu.route("/followed_user", methods=["POST"])
@user_login
def followed_user():
    """关注或者取消关注"""
    # 0. 取到自己的登录信息
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="未登录")
    # 1.取参数
    user_id = request.json.get("user_id")
    action = request.json.get("action")
    # 2. 判断参数
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ["follow", "unfollow"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 取到要被关注的用户
    try:
        author = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    if not author:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    # 4. 根据要执行的操作去修改对应的数据
    if action == "follow":
        # if user not in author.followers:
        # 如果用户不在作者的粉丝中
        # 往作者的粉丝中添加一个用户
        if user not in author.followers:
            author.followers.append(user)
    else:
        # 取消关注
        # 如果用户在作者的粉丝中
        # 作者的粉丝中需要移除用户
        if user in author.followers:
            author.followers.remove(user)
        else:
            return jsonify(errno=RET.DATAEXIST, errmsg="当前用户未被关注")

    return jsonify(errno=RET.OK, errmsg="操作成功")


@new_blu.route("/comment_like", methods=["POST"])
@user_login
def set_comment_like():
    """
    评论点赞数
    1、接收参数 comment_id action
    2、校验参数
    3、CommentLike()往点赞的表中添加或者删除一条数据
    4、返回响应
    :return:
    """

    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 获取点赞数
    try:
        comment_obj = Comment.query.get(comment_id)  # type: Comment
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not comment_obj:
        return jsonify(errno=RET.NODATA, errmsg="该条评论不存在")

    comment_like_obj = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                CommentLike.user_id == user.id).first()
    if action == "add":
        # 如果是添加一条评论，要初始化一个评论对象，并将数据添加进去
        # 如果存在代表该用户已经点过赞了就不能添加赞
        if not comment_like_obj:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            # db.session.commit()
            comment_obj.like_count += 1
    else:
        # 如果这条点赞存在，才能删除点赞
        if comment_like_obj:
            db.session.delete(comment_like_obj)
            # db.session.commit()
            comment_obj.like_count -= 1
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")


@new_blu.route("/news_comment", methods=["POST"])
@user_login
def news_comment():
    """
    新闻评论功能
    1、接收参数 用户 新闻 评论内容 parent_id
    2、校验参数
    3、业务逻辑， 往数据库中添加一条评论
    4、返回响应
    :return:
    """
    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get("news_id")
    comment_str = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该条新闻不存在")

    # 添加新闻评论， 往评论表中添加评论
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg="数据库保存失败")

    comments = news.comments.count()

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict(), comments=comments)


@new_blu.route("/news_collect", methods=["POST"])
@user_login
def news_collect():
    """
    新闻收藏和取消收藏功能
    1、接收参数
    2、校验参数
    3、收藏新闻和取消收藏
    4、返回响应
    :return:
    """

    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="数据格式不正确")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该条新闻不存在")

    # 执行具体业务
    if action == "collect":
        # 当我们去收藏一条新闻的时候，我们应该先去判断该用户书否收藏过该条新闻，如果没有收藏过，才去添加
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        # 当我们去取消收藏的时候，如果该新闻在你的收藏列表中，才去删除
        if news in user.collection_news:
            user.collection_news.remove(news)

    return jsonify(errno=RET.OK, errmsg="OK")


@new_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    详情页渲染
    :param news_id:
    :return:
    """
    user = g.user

    # 1.点击排行
    clicks_news = []
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
    news_dict_list = [new_obj.to_basic_dict() for new_obj in clicks_news]

    # 新闻详情
    if not news_id:
        abort(404)

    news = None  # type: News
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    if not news:
        abort(404)

    news.clicks += 1

    # 详情页收藏和已收藏是由is_collected
    is_collected = False
    # 在什么样的一个情况下  is_collected = True
    # 需求：如果 该用户收藏了该条新闻 is_collected = True
    # 1、保证用户存在
    # 2、新闻肯定存在
    # 3、该条新闻在用户收藏新闻的列表中
    # 4、用户收藏新闻的列表----> user.collection_news.all()  [news, news]
    if user and news in user.collection_news.all():
        is_collected = True

    is_followed = False

    # 用户关注者
    author = news.user
    if user and author:
        # 课件中的代码有bug
        # 1、如果user在author的粉丝中
        # 2、如果author在user的关注者中  if author in user.followed:
        if user in author.followers:
            is_followed = True

    # 四、查询数据 该条新闻下的所有评论
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    # # 用户不存在不用显示
    # if user:
    #     # 查询出所有的评论id
    #     comment_ids = [comment.id for comment in comments]
    #     # 查询出那些评论id是被该用户点过赞的
    #     comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id,
    #                                              CommentLike.comment_id.in_(comment_ids)).all()
    #     comment_likes_ids = [comment_likes_obj.comment_id for comment_likes_obj in comment_likes]

    comments_dict_li = []
    for comment in comments:
        comment_dict = comment.to_dict()
        comment_dict["is_like"] = False
        # 如果comment_dict["is_like"] = True代表已经点赞
        # 如果该条评论的id在我的点赞评论id列表中
        if user and CommentLike.query.filter(CommentLike.comment_id == comment.id,
                                             CommentLike.user_id == user.id).first():
            comment_dict["is_like"] = True
        comments_dict_li.append(comment_dict)

    data = {
        "user": user.to_dict() if user else None,
        "news_dict_list": news_dict_list,
        "news": news.to_dict(),
        "is_collected": is_collected,
        "comments": comments_dict_li,
        "is_followed": is_followed
    }
    return render_template("news/detail.html", data=data)
