from flask import g, jsonify
from flask import render_template
from flask import request

from my_news import db
from my_news.constants import CLICK_RANK_MAX_NEWS
from my_news.utils.common import user_login_data
from my_news.models import News, Comment, CommentLike, User
from my_news.utils.response_code import RET
from . import news_blue



@news_blue.route('/followed_user', methods=['GET', 'POST'])
@user_login_data
def followed_user():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='请先登录')
    action = request.json.get('action')
    other_id = request.json.get('user_id')
    if not all([action, other_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    other_user = User.query.get(other_id)
    if action == 'follow':
        if other_user not in user.followed:
            user.followed.append(other_user)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg='已经关注过了')
    else:
        if other_user in user.followed:
            user.followed.remove(other_user)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg='已经取消关注过了')
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='OK')


@news_blue.route('/comment_like', methods=['GET', 'POST'])
@user_login_data
def comment_like():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='请先登录')
    comment_id = request.json.get('comment_id')
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not all([comment_id, news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    comment = Comment.query.get(comment_id)
    commentLike_obj = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                               CommentLike.user_id == user.id).first()
    if action == 'add':
        if not commentLike_obj:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = user.id
            db.session.add(comment_like)
            comment.like_count += 1
    else:
        if commentLike_obj:
            db.session.delete(commentLike_obj)
            comment.like_count -= 1
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='OK')


@news_blue.route('/news_comment', methods=['GET', 'POST'])
@user_login_data
def news_comment():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='请先登录')
    news_id = request.json.get('news_id')
    content = request.json.get('comment')
    parent_id = request.json.get('parent_id')
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id
    db.session.add(comment)
    db.session.commit()

    return jsonify(errno=RET.OK, errmsg='OK', data=comment.to_dict())


@news_blue.route('/news_collect', methods=["GET", "POST"])
@user_login_data
def news_collect():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='请先登录')
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    news = News.query.get(news_id)
    if action == 'collect':
        if news not in user.collection_news:
            user.collection_news.append(news)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg='已经收藏过了')
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg='已经取消收藏过了')
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='OK')


@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    user = g.user
    news_click_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    click_news_list = []
    for news in news_click_list if news_click_list else []:
        click_news_list.append(news.to_dict())

    news = News.query.get(news_id)

    is_collected = False
    is_followed = False
    comment_list = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    comments = []
    if user:
        if news in user.collection_news:
            is_collected = True
        if news.user in user.followed:
            is_followed = True
        user_comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
        user_comment_ids = [comment_like.comment_id for comment_like in user_comment_likes]
        for comment in comment_list if comment_list else []:
            comment_dict = comment.to_dict()
            comment_dict['is_like'] = False
            if comment.id in user_comment_ids:
                comment_dict['is_like'] = True
            comments.append(comment_dict)

    # comment_list = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    # comments = []
    # if user:
    #     user_comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
    #     user_comment_ids = [comment_like.comment_id for comment_like in user_comment_likes]
    #     for comment in comment_list if comment_list else []:
    #         comment_dict = comment.to_dict()
    #         comment_dict['is_like'] = False
    #         if comment.id in user_comment_ids:
    #             comment_dict['is_like'] = True
    #         comments.append(comment_dict)

    data = {
        'click_news_list': news_click_list,
        'user_info': user.to_dict() if user else None,
        'news': news.to_dict() if news else None,
        'is_collected': is_collected,
        'comments': comments,
        'is_followed': is_followed,
    }
    return render_template('news/detail.html', data=data)
