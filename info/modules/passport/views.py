import json
import random

import re
from flask import request, abort, current_app, make_response, jsonify

from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha

# 1、请求方式是什么
# 2、请求的url是什么
# 3、参数的名字是什么
# 4、返回给前端的参数和参数类型是什么
from info.utils.response_code import RET


@passport_blu.route("/sms_code", methods=['POST'])
def get_sms_code():
    """
    1.接受参数 mobile  image_code image_code_id
    2、校验参数：mobile  正则
    3、校验用户输入的验证码和通过image_code_id查询出来的验证码是否一致
    4、先去定义一个随机的6验证码
    5、调用云通讯发送手机验证码
    6、将验证码保存到reids
    7、给前端一个响应
    :return:
    """
    # 接受的数据是json格式的字符串要转化成字典格式
    # json_data = request.data
    # dict_data = json.loads(json_data)

    dict_data = request.json

    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 先判断参数是否齐全,做全局判断
    # 返回json格式的参数
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 正则判断电话号码
    if not re.match(r"1[3579]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入正确的手机号")

    # 判断验证码是否一致
    try:
        real_image_code = redis_store.get("ImageCodeId" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")

    if not real_image_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码已经过期")

    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码不正确")

    # 核心逻辑 5、先去定义一个随机的6位验证码,
    # "%06d" 将一个数字转化为6位数字，如果位数不够，用0填充   1234   001234
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.info("短信验证码为%s" % sms_code_str)

    result = CCP().send_template_sms('17600823404', [sms_code_str, constants.IMAGE_CODE_REDIS_EXPIRES / 5], 1)
    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg="验证码发送错误")

    # 将sms_code写入redis数据库
    try:
        redis_store.setex("sms_"+str(mobile), constants.IMAGE_CODE_REDIS_EXPIRES, sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机验证码保存失败")

    return jsonify(errno=RET.OK, errmsg="成功发送短信验证码")


@passport_blu.route("/image_code")
def get_image_code():
    """
        /passport/image_code?imageCodeId=c1a16ab9-31d7-4a04-87c2-57c01c303828
        1、接收参数（随机的字符串）
        2、校验参数是否存在
        3、生成验证码  captche
        4、把随机的字符串和生成的文本验证码以key，value的形式保存到redis
        5、把图片验证码返回给浏览器
        :return:
    """
    # 1、接收参数（随机字符）
    image_code_id = request.args.get("imageCodeId")

    # 2、校验参数是否存在
    if not image_code_id:
        abort(404)

    # 3、生成验证码 captcha
    _, text, image = captcha.generate_captcha()

    # 4、把随机字符串和生成的文本验证码以key, value的形式保存到redis
    try:
        redis_store.setex("ImageCodeId" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response
