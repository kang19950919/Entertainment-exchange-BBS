from logging.handlers import RotatingFileHandler
import logging
from flask import Flask, g, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from redis import StrictRedis

from config import config  # 将字典导入

# config = {
#     "develop": DevelopConfig,
#     "product": ProductConfig,
#     "testing": TestingConfig
# }

# db = SQLAlchemy(app) # 拆分成两步
# db = SQLAlchemy()
# db.init_app(app)
from utils.common import do_index_class, user_login

db = SQLAlchemy()


def set_log(config_name):
    # 通过不同的人配置创建出不同日志记录
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


redis_store = None  # type: StrictRedis


# 只要是可变的参数，一、可以放在配置文件中，二、用函数封装 三、用全局变量
# 可所有可变的参数用函数的形参来代替
def create_app(config_name):
    set_log(config_name)
    app = Flask(__name__)
    # 一、集成配置类
    app.config.from_object(config[config_name])

    # 二、集成sqlalchemy到flask
    db.init_app(app)

    # 三、集成redis  可以吧容易产生变化的值放入到配置中
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_host, port=config[config_name].REDIS_port, db=0, decode_responses=True)

    # 四、CSRFProtect, 只起到保护的作用
    # 向cookie中写入CSRF_Token
    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response

    @app.errorhandler(404)
    @user_login
    def get_404_error(e):
        data = {
            "user": g.user.to_dict() if g.user else None
        }
        return render_template("news/404.html", data=data)

    CSRFProtect(app)

    # 添加自定义过滤器
    app.add_template_filter(do_index_class, "index_class")

    # 注册蓝图
    # 对于只是用一次的数据，什么时候用什么时候导入进来
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    from info.modules.news import new_blu
    app.register_blueprint(new_blu)
    from info.modules.profile import profile_blu
    app.register_blueprint(profile_blu)
    from info.modules.admin import admin_blu
    app.register_blueprint(admin_blu)

    # 集成flask-session
    Session(app)

    return app
