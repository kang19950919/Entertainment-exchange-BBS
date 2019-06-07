from redis import StrictRedis


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
