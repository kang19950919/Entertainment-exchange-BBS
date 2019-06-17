import logging

from redis import StrictRedis


class Config(object):
    SECRET_KEY = "1234567890"

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/bbs2"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # TODO 设置数据库的默认提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # redis配置
    REDIS_host = "127.0.0.1"
    REDIS_port = 6379

    # 指定session的储存方式
    SESSION_TYPE = "redis"
    # 指定储存session的储存对象
    SESSION_REDIS = StrictRedis(host=REDIS_host, port=REDIS_port, db=0)
    # 设置session签名  加密
    SESSION_SIGNER = True
    # 如果为False cookie的存活时间为浏览器关闭时，如果为True，cookie的过期时间和session一样
    SESSION_PERMANENT = True
    # 设置session保存的时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2


# 我们往往在工作中，不仅仅有一个配置文件。生产环境有生产环境的配置，开发环境有开发环境的配置，测试环境有测试环境的
# 不管是开发环境还是测试环境总有一些配置是相同。所以说可以吧config作为基类
# 面向对象的继承
class DevelopConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.ERROR


class TestingConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


# 使用字典去封装
config = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "testing": TestingConfig
}