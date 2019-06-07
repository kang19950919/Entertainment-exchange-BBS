"""
一、集成配置类
二、集成sqlalchemy到flask
三、集成redis
四、集成csrfprotect
五、集成flask-session
六、集成flask-script
七、集成flask-migrate
"""
from flask_migrate import MigrateCommand, Migrate
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager


class Config(object):
    SECRET_KEY = "1234567890"
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:chuanzhi@127.0.0.1:3306/information_bj38"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 给配置类里面自定义了两个类属性
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 指定session的储存方式
    SESSION_TYPE = "redis"
    # 指定储存session的储存对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置session签名  加密
    SESSION_USE_SIGNER = True
    # 设置session永久保存
    SESSION_PERMANENT = False
    # 设置session保存的时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2


app = Flask(__name__)
# 一、集成配置类
app.config.from_object(Config)

# 二、集成sqlalchemy到flask
db = SQLAlchemy(app)

# 三、集成redis  可以吧容易产生变化的值放入到配置中
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 四、CSRFProtect, 只起到保护的作用，具体往表单和cookie中设置csrf_token还需要我们自己去做
CSRFProtect(app)

# 集成flask-session
# 说明: flask中的session是保存用户数据的容器（上下文），而flask_session中的Session是指定session的保存路径
Session(app)

# 六、集成flask-script
manager = Manager(app)

# 七、集成flask-migrate, 在flask中对数据库进行迁移
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@app.route("/")
def index():
    # 设置一个session，如果在redis中能够获取到session的值，那么说明已经成功将flask-session集成到flask中
    session["name"] = "hahahaha"
    return "Hello World"


if __name__ == "__main__":
    manager.run()