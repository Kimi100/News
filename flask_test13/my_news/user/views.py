from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request

from my_news.models import Category, News, User
from my_news.utils.image_storage import storage
from my_news import db
from my_news.utils.response_code import RET
from . import user_blue
from my_news.utils.common import user_login_data
from my_news.constants import *


@user_blue.route('/other_news_list')
def other_news_list():
    try:
        p = int(request.args.get('p'))
    except:
        p = 1
    user_id = request.args.get('user_id')
    paginate = News.query.filter(News.user_id == user_id).paginate(p, OTHER_NEWS_PAGE_MAX_COUNT, False)
    news_list = []
    news_items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    print(paginate.page)
    for news in news_items if news_items else []:
        news_list.append(news.to_dict())
    data = {
        'news_list': news_list,
        'current_page': current_page,
        'total_page': total_page,
    }
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


@user_blue.route('/other_info')
@user_login_data
def other_info():
    user = g.user
    other_id = request.args.get('id')
    other_user = User.query.get(other_id)
    is_followed = False
    if user:
        if other_user in user.followed:
            is_followed = True
    data = {
        'user_info': user.to_dict() if user else None,
        'other_info': other_user.to_dict() if other_user else None,
        'is_followed': is_followed,
    }
    return render_template('news/other.html', data=data)


@user_blue.route('/follow')
@user_login_data
def follow():
    user = g.user
    if not user:
        return redirect('/')
    try:
        p = int(request.args.get('p'))
    except:
        p = 1
    paginate = user.followed.paginate(p, USER_FOLLOWED_MAX_COUNT, False)
    user_items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    users = []
    for user in user_items if user_items else []:
        users.append(user.to_dict())

    data = {
        'users': users,
        'current_page': current_page,
        'total_page': total_page,
    }
    return render_template('news/user_follow.html', data=data)


@user_blue.route('/news_list')
@user_login_data
def news_list():
    user = g.user
    if not user:
        return redirect('/')
    try:
        p = int(request.args.get('p', 1))
    except:
        p = 1
    paginate = user.news_list.paginate(p, USER_NEWS_MAX_COUNT, False)
    news_items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages
    news_list = []
    for news in news_items if news_items else []:
        news_list.append(news.to_review_dict())
    data = {
        'news_list': news_list,
        'total_page': total_page,
        'current_page': current_page,
    }
    return render_template('news/user_news_list.html', data=data)


@user_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    user = g.user
    if request.method == "GET":
        if not user:
            return redirect('/')
        category_list = Category.query.all()
        categories = []
        for category in category_list if category_list else []:
            categories.append(category.to_dict())
        categories.pop(0)
        data = {
            'categories': categories,
        }
        return render_template('news/user_news_release.html', data=data)

    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    index_image = request.files.get('index_image')
    content = request.form.get('content')
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    image = index_image.read()
    key_url = storage(image)
    news = News()
    print(content)
    news.title = title
    news.source = '个人用户'
    news.user_id = user.id
    news.status = 1
    news.category_id = category_id
    news.digest = digest
    news.index_image_url = QINIU_DOMIN_PREFIX + key_url
    news.content = content
    db.session.add(news)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='发布新闻成功')


@user_blue.route('/collection')
@user_login_data
def collection():
    user = g.user
    if not user:
        return redirect('/')
    try:
        p = int(request.args.get('p', 1))
    except:
        p = 1
    paginate = user.collection_news.paginate(p, USER_COLLECTION_MAX_NEWS, False)
    news_items = paginate.items
    total_page = paginate.page
    current_page = paginate.page
    collections = []
    for news in news_items if news_items else []:
        collections.append(news.to_dict())
    data = {
        'collections': collections,
        'current_page': current_page,
        'total_page': total_page,
    }
    return render_template('news/user_collection.html', data=data)


@user_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    user = g.user
    if request.method == "GET":
        if not user:
            return redirect('/')
        return render_template('news/user_pass_info.html')
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg='请输入正确的密码')
    user.password = new_password
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='修改成功')


@user_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":
        if not user:
            return redirect('/')
        data = {
            'user_info': user.to_dict() if user else None
        }
        return render_template('news/user_pic_info.html', data=data)
    avatar = request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='请传入图片')
    image = avatar.read()
    key = storage(image)
    if not key:
        return jsonify(errno=RET.THIRDERR, errmsg='第三方系统出现问题')
    user.avatar_url = key
    db.session.commit()
    data = {
        'avatar_url': QINIU_DOMIN_PREFIX + key
    }
    return jsonify(errno=RET.OK, errmsg='设置成功', data=data)


@user_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    user = g.user
    if request.method == 'GET':
        if not user:
            return redirect('/')
        data = {
            'user_info': user.to_dict() if user else None
        }
        return render_template('news/user_base_info.html', data=data)
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='设置基资料成功')


@user_blue.route('/info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect('/')
    data = {
        'user_info': user.to_dict() if user else None,
    }
    return render_template('news/user.html', data=data)
