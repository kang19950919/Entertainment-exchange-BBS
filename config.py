import logging

from redis import StrictRedis


class Config(object):
    SECRET_KEY = "1234567890"

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/BBS"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 给配置类里面自定义了两个类属性
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 指定session的储存方式
    SESSION_TYPE = "redis"
    # 指定储存session的储存对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    # 设置session签名  加密
    SESSION_USE_SIGNER = True
    # 设置session永久保存
    SESSION_PERMANENT = False
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


# 将类封装到字典中
config = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "testing": TestingConfig
}