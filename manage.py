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
from config import Config


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
    return "Hello World"


if __name__ == "__main__":
    manager.run()
