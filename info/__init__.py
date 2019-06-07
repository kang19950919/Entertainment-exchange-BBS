#  创建一个存放业务逻辑包
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from config import config

db = SQLAlchemy()


# 只要是可变的参数，一、可以放在配置文件中，二、用函数封装 三、用全局变量
# 可所有可变的参数用函数的形参来代替
def create_app(config_name):
    app = Flask(__name__)
    # 一、集成配置类
    app.config.from_object(config["develop"])

    # 二、集成sqlalchemy到flask
    db.init_app(app)

    # 三、集成redis  可以吧容易产生变化的值放入到配置中
    redis_store = StrictRedis(host=config["develop"].REDIS_HOST, port=config["develop"].REDIS_PORT)

    # 四、CSRFProtect, 只起到保护的作用，具体往表单和cookie中设置csrf_token还需要我们自己去做
    CSRFProtect(app)

    # 集成flask-session
    # 说明: flask中的session是保存用户数据的容器（上下文），而flask_session中的Session是指定session的保存路径
    Session(app)

    return app
