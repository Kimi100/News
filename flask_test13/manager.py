from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from my_news import create_app, db
from my_news import models
from my_news.models import User

app = create_app('development')
manager = Manager(app)
Migrate(app, db)
manager.add_command('mysql', MigrateCommand)

@manager.option('-n', '--name', dest='name')
@manager.option('-p', '--password', dest='password')
def create_admin(name, password):
    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    print(app.url_map)
    manager.run()
