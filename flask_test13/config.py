import redis


class Config(object):
    DEBUG = True
    SECRET_KEY = 'aisoawroiho'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/db_test6'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True
    REDIS_HOST = '127.0.0.1'
    REDIS_POST = 6379
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_POST)
    SESS_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600


class DevelopmentConfig(Config):
    DEBUG = True


class ProduactionConfig(Config):
    DEBUG = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProduactionConfig,
}
