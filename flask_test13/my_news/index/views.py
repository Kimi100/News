from flask import g
from flask import render_template, current_app, jsonify
from flask import request
from flask import session

from my_news.constants import *
from my_news.models import User, Category, News
from my_news.utils.common import user_login_data
from my_news.utils.response_code import RET
from . import index_blue


@index_blue.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')


@index_blue.route('/news_list')
def news_list():
    try:
        cid = int(request.args.get('cid'))
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
    except:
        cid = 1
        page = 1
        per_page = 10

    if not all([cid, per_page]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    filter = [News.status == 0]
    if cid != 1:
        filter.append(News.category_id == cid)
    paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page, per_page, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_dict_list = []
    for item in items:
        news_dict_list.append(item.to_dict())
    data = {
        'current_page': current_page,
        'total_page': total_page,
        'news_dict_li': news_dict_list,
    }
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


@index_blue.route('/')
@user_login_data
def index():
    user = g.user

    news_click_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    click_news_list = []
    for news in news_click_list if news_click_list else []:
        click_news_list.append(news.to_dict())

    category_lsit = Category.query.all()
    categories = []
    for category in category_lsit if category_lsit else []:
        categories.append(category.to_dict())

    data = {
        'user_info': user.to_dict() if user else None,
        'click_news_list': click_news_list,
        'categories': categories,
    }

    return render_template('news/index.html', data=data)
