import datetime

import random

from my_news import db
from my_news.models import User
from manager import app


def add_test_users():
    users = []
    now = datetime.datetime.now()
    for num in range(0, 10000):
        try:
            user = User()
            user.nick_name = "%011d" % num
            user.mobile = "%011d" % num
            user.password_hash = "pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829"
            user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            users.append(user)
            print(user.mobile)
        except Exception as e:
            print(e)
    # 手动开启一个app的上下文
    with app.app_context():
        db.session.add_all(users)
        db.session.commit()
    print('OK')


if __name__ == '__main__':
    add_test_users()