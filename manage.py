"""
一、集成配置类
二、集成sqlalchemy到flask
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    DUBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/bbs"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app = Flask(__name__)
# 一、集成配置类
app.config.from_object(Config)

# 二、集成sqlalchemy到flask
db = SQLAlchemy(app)


@app.route("/")
def index():
    return "你好,世界"


if __name__ == '__main__':
    app.run()
