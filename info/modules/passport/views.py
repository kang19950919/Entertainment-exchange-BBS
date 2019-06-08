import json

from flask import request, abort, current_app, make_response

from info import redis_store, constants
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha


# 1、请求方式是什么
# 2、请求的url是什么
# 3、参数的名字是什么
# 4、返回给前端的参数和参数类型是什么
# @passport_blu.route("/sms_code", methods=['POST'])
# def get_sms_code():
#     """
#     1.接受参数 mobile  image_code image_code_id
#
#     :return:
#     """
#     # 接受的数据是json格式的字符串要转化成字典格式
#     # json_data = request.data
#     # dict_data = json.loads(json_data)
#
#     dict_data = request.json
#
#     mobile = dict_data.get("mobile")
#     image_code = dict_data.get("image_code")
#     image_code_id = dict_data.get("image_code_id")
#
#     # 核心逻辑 发送验证码
#     if not all([mobile, image_code, image_code_id])


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
        redis_store.setex("ImageCodeId"+image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response
