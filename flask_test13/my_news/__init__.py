import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect,generate_csrf

from config import config_map

db = SQLAlchemy()
redis_store = None

def create_app(config_name):
    app = Flask(__name__)
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)
    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_POST, decode_responses=True)

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response

    from my_news.utils.common import do_index_class
    app.add_template_filter(do_index_class, 'indexClass')

    from my_news.index import index_blue
    app.register_blueprint(index_blue)

    from my_news.passport import passport_blue
    app.register_blueprint(passport_blue)

    from my_news.news import news_blue
    app.register_blueprint(news_blue)

    from my_news.user import user_blue
    app.register_blueprint(user_blue)

    from my_news.admin import admin_blue
    app.register_blueprint(admin_blue)

    CSRFProtect(app)
    Session(app)
    return app