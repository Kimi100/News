from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
import time
from datetime import datetime, timedelta
from my_news.utils.image_storage import storage
from my_news import db
from my_news.models import User, News, Category
from my_news.utils.common import user_login_data
from my_news.utils.response_code import RET
from . import admin_blue
from my_news.constants import *

@admin_blue.route('/add_category', methods=['GET', 'POST'])
@user_login_data
def add_category():
    user = g.user
    if not user or not user.is_admin:
        return redirect(url_for('admin.login'))
    name = request.json.get('name', None)
    cid = request.json.get('id', None)

    if cid:
        category = Category.query.get(cid)
        category.name = name
    else:
        category = Category()
        category.name = name
        db.session.add(category)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='OK')


@admin_blue.route('/news_type')
@user_login_data
def news_type():
    user = g.user
    if not user or not user.is_admin:
        return redirect(url_for('admin.login'))
    category_list = Category.query.all()
    categories = []
    for category in category_list if category_list else []:
        categories.append(category.to_dict())
    categories.pop(0)
    data = {
        'categories': categories,
    }
    return render_template('admin/news_type.html', data=data)


@admin_blue.route('/news_edit_detail', methods=['GET', 'POST'])
@user_login_data
def news_edit_detail():
    user = g.user
    if request.method == 'GET':
        if not user or not user.is_admin:
            return redirect(url_for('admin.login'))
        news_id = request.args.get('news_id')
        news = News.query.get(news_id)
        category_list = Category.query.all()
        categories = []
        for category in category_list if category_list else []:
            categories.append(category.to_dict())
        categories.pop(0)
        data = {
            'news': news.to_dict() if news else None,
            'categories': categories,
        }
        return render_template('admin/news_edit_detail.html', data=data)
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    index_image = request.files.get('index_image')
    content = request.form.get('content')
    news_id = request.form.get('news_id')
    if not all([title, category_id, digest, index_image, content, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    news = News.query.get(news_id)
    image = index_image.read()
    print(image)
    image_key = storage(image)
    news.title = title
    news.digest = digest
    news.category_id = category_id
    news.index_image_url = QINIU_DOMIN_PREFIX + image_key
    news.content = content
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='编辑成功')


@admin_blue.route('/news_edit')
@user_login_data
def news_edit():
    user = g.user
    if not user or not user.is_admin:
        return redirect(url_for('admin.login'))
    try:
        p = int(request.args.get('p'))
    except:
        p = 1
    keywords = request.args.get('keywords')
    filter = [News.status == 0]
    if keywords:
        filter.append(News.title.contains(keywords))
    paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(p, ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                     False)

    news_items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_list = []

    for news in news_items if news_items else []:
        news_list.append(news.to_dict())

    data = {
        'news_list': news_list,
        'current_page': current_page,
        'total_page': total_page,
    }
    return render_template('admin/news_edit.html', data=data)


@admin_blue.route('/news_review_detail', methods=['GET', 'POST'])
@user_login_data
def news_review_detail():
    user = g.user
    if request.method == 'GET':
        if not user or not user.is_admin:
            return redirect(url_for('admin.login'))
        news_id = request.args.get('news_id')
        news = News.query.get(news_id)
        data = {
            'news': news.to_dict() if news else None,
        }
        return render_template('admin/news_review_detail.html', data=data)
    action = request.json.get('action')
    news_id = request.json.get('news_id')
    if not all([action, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    news = News.query.get(news_id)
    if action == 'accept':
        news.status = 0
    else:
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
        news.reason = reason
        news.status = -1
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='审核OK')


@admin_blue.route('/news_review')
@user_login_data
def news_review():
    user = g.user
    if not user or not user.is_admin:
        return redirect(url_for('admin.login'))
    try:
        p = int(request.args.get('p'))
    except:
        p = 1
    keywords = request.args.get('keywords')
    filter = [News.status != 0]
    if keywords:
        filter.append(News.title.contains(keywords))
    paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(p, ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                     False)
    news_items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    news_list = []
    for news in news_items if news_items else []:
        news_list.append(news.to_dict())
    data = {
        'news_list': news_list,
        'current_page': current_page,
        'total_page': total_page,
    }
    return render_template('admin/news_review.html', data=data)


@admin_blue.route('/user_list')
@user_login_data
def user_list():
    user = g.user
    if not user or not user.is_admin:
        return redirect(url_for('admin.login'))
    try:
        p = int(request.args.get('p'))
    except:
        p = 1
    paginate = User.query.order_by(User.last_login.desc()).paginate(p, ADMIN_USER_PAGE_MAX_COUNT, False)
    user_items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    users = []
    for user in user_items if user_items else []:
        users.append(user.to_admin_dict())
    data = {
        'users': users,
        'current_page': current_page,
        'total_page': total_page,
    }
    return render_template('admin/user_list.html', data=data)


@admin_blue.route('/user_count')
@user_login_data
def user_count():
    user = g.user
    if not user or not user.is_admin:
        return redirect(url_for('admin.login'))

    total_count = User.query.filter(User.is_admin == False).count()

    t = time.localtime()
    new_time_mon = '%0d-%02d-01' % (t.tm_year, t.tm_mon)
    mon_begin = datetime.strptime(new_time_mon, '%Y-%m-%d')
    mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin).count()

    new_time_today = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    today_begin = datetime.strptime(new_time_today, '%Y-%m-%d')
    day_count = User.query.filter(User.is_admin == False, User.create_time >= today_begin).count()

    active_date = []
    active_count = []
    for i in range(0, 31):
        begin_date = today_begin - timedelta(days=i)
        end_date = today_begin - timedelta(days=(i - 1))
        count = User.query.filter(User.is_admin == False, User.create_time >= begin_date,
                                  User.create_time < end_date).count()
        active_count.append(count)
        active_date.append(begin_date.strftime('%Y-%m-%d'))
    active_date.reverse()
    active_count.reverse()
    data = {
        'total_count': total_count,
        'mon_count': mon_count,
        'day_count': day_count,
        'active_count': active_count,
        'active_date': active_date,
    }

    return render_template('admin/user_count.html', data=data)


@admin_blue.route('/logout')
@user_login_data
def logout():
    user = g.user
    if not user or not user.is_admin:
        return redirect(url_for('admin.login'))
    session.pop('user_mobile')
    session.pop('user_id')
    session.pop('user_is_admin')
    return redirect(url_for('admin.login'))


@admin_blue.route('/index')
@user_login_data
def index():
    user = g.user
    if not user or not user.is_admin:
        return redirect(url_for('admin.login'))
    return render_template('admin/index.html', user=user.to_admin_dict())


@admin_blue.route('/login', methods=['GET', 'POST'])
@user_login_data
def login():
    if request.method == 'GET':
        user = g.user
        if user and user.is_admin:
            return redirect(url_for('admin.index'))
        return render_template('admin/login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='请输入参数')
    user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    if not user:
        return render_template('admin/login.html', errmsg='用户不存在, 或者该用户没有权限')
    if not user.check_password(password):
        return render_template('admin/login.html', errmsg='请输入正确的密码')
    session['user_id'] = user.id
    session['user_mobile'] = user.mobile
    session['user_is_admin'] = user.is_admin
    return redirect(url_for('admin.index'))
