import random
import re

from flask import session

from my_news.libs.yuntongxun.sms import CCP
from flask import make_response, jsonify
from flask import request
from my_news import redis_store, db
from my_news.models import User
from my_news.utils.captcha.captcha import captcha
from my_news.utils.response_code import RET
from . import passport_blue
from my_news.constants import *


@passport_blue.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id')
    session.pop('user_name')
    session.pop('user_mobile')
    return jsonify(errno=RET.OK, errmsg='退出成功')


@passport_blue.route('/login', methods=['GET', 'POST'])
def login():
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    if not re.match(r'1[^269]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的电话号码')
    user = User.query.filter(User.mobile == mobile).first()
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='没有此账号, 请先注册')
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg='请输入正确的密码')
    session['user_id'] = user.id
    session['user_name'] = user.nick_name
    session['user_mobile'] = user.mobile
    return jsonify(errno=RET.OK, errmsg='登录成功')


@passport_blue.route('/register', methods=['GET', 'POST'])
def register():
    mobile = request.json.get('mobile')
    smscode = request.json.get('smscode')
    password = request.json.get('password')
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    if not re.match(r'1[^269]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的电话号码')
    redis_sms_code = redis_store.get('random_sms_' + mobile)
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')
    if redis_sms_code != smscode:
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的短信验证码')
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    db.session.add(user)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='注册成功')


@passport_blue.route('/sms_code', methods=['GET', 'POST'])
def send_sms_code():
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入参数')
    if not re.match(r'1[^269]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的电话号码')
    redis_image_code = redis_store.get('image_code_' + image_code_id)
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    if redis_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg='请输入正确的图片验证码')
    random_sms = '%06d' % random.randint(0, 999999)
    # status_code = CCP().send_template_sms(mobile, [random_sms, 2], 1)
    # if status_code != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg='第三方系统错误')
    redis_store.set('random_sms_' + mobile, random_sms, SMS_CODE_REDIS_EXPIRES)
    print('图片验证码为: %s' % random_sms)
    return jsonify(errno=RET.OK, errmsg='发送短信成功')


@passport_blue.route('/image_code')
def send_image():
    code_id = request.args.get('code_id')
    name, text, image = captcha.generate_captcha()
    redis_store.set('image_code_' + code_id, text, IMAGE_CODE_REDIS_EXPIRES)
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/jpg'
    print('图片验证码为: %s' % text)
    return resp
