import random
import re
from datetime import datetime

from flask import request, abort, current_app, jsonify, make_response, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from utils.captcha.captcha import captcha

from info.modules.passport import passport_blu
from utils.response_code import RET


@passport_blu.route("/logout")
def logout():
    """
    直接删除session
    :return:
    """
    session.pop("user_id", None)
    session.pop("is_admin", None)
    return jsonify(errno=RET.OK, errmsg="OK")


@passport_blu.route("/login", methods=["POST"])
def login():
    """
    1、接收参数
    2、校验参数  手机号格式  密码是否正确
    3、保持用户登录状态
    5、设置用户登录时间last_login
    4、返回响应
    :return:
    """
    dict_data = request.json
    mobile = dict_data.get("mobile")
    password = dict_data.get("password")

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

        # 3、mobile  正则
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号的格式不正确")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户没有注册")

    if not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg="密码输入错误")

    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登录成功")


@passport_blu.route("/register", methods=["POST"])
def register():
    """
    1、接收参数 mobile smscode password
    2、整体校验参数的完整性
    3、手机号格式是否正确
    4、从redis中通过手机号取出真是的短信验证码
    5、和用户输入的验证码进行校验
    6、初始化User()添加数据
    7、session保持用户登录状态
    8、返回响应
    :return:
    """
    # 1、接收参数
    dict_data = request.json
    mobile = dict_data.get("mobile")
    smscode = dict_data.get("smscode")
    password = dict_data.get("password")

    # 2、整体校验参数的完整性
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 3、mobile  正则
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号的格式不正确")

    # 4、从redis中通过手机号取出真是的短信验证码
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已经过期")

    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 核心逻辑
    user = User()
    user.nick_name = "kk" + mobile
    user.mobile = mobile
    # 这是实例方法经过装饰器装饰，里面有哈希加密
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 7、session保持用户登录状态
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():
    """
    1、接收参数为json格式： mobile， image_code， image_code_id
    2、校验参数：mobile  正则
    3、校验用户输入的验证码和通过image_code_id查询出来的验证码是否一致
    4、先去定义一个随机的6验证码
    5、调用云通讯发送手机验证码
    6、将验证码保存到reids
    7、给前端一个响应
    :return:
    """
    dict_data = request.json

    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 校验参数
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不正确")

    # 正则 手机号
    if not re.match(r"1[35789]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号不正确")

    # 校验验证码, 从数据库取出图片验证码
    try:
        real_image_code = redis_store.get("imageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败哦")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")

    if real_image_code != image_code:
        return jsonify(errno=RET.PARAMERR, errmsg="验证码错误")

    # 发送短信验证码
    # 生成六位验证码
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.info("短信验证码是:%s" % sms_code_str)

    # result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/5], 1)
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="验证码发送失败")

    # 将验证码保存到redis数据库中
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="成功发送短信验证码")


@passport_blu.route("/image_code")
def get_image_code():
    """
    1.接收参数（随机的字符串）
    2.验证参数是否存在
    3.生成验证码
    4.把随机生成的字符串和文本验证码以key，value的形式存储到redis数据库
    5.把图片验证码返回给浏览器
    :return:
    """
    # 1、接收参数
    image_code_id = request.args.get("imageCodeId")

    # 2、验证参数
    if not image_code_id:
        abort(404)

    # 3、生成验证码
    _, text, image = captcha.generate_captcha()
    current_app.logger.info("验证码是:%s" % text)

    # 4、把随机生成的字符串和文本验证码以key，value的形式存储到redis数据库
    try:
        redis_store.setex("imageCodeId_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5、把图片验证码返回给浏览器
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response
