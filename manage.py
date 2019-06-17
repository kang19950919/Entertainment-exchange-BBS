"""
一、集成配置类
二、集成sqlalchemy到flask
三、集成redis
四、集成csrfprotect
五、集成flask-session
六、集成flask-script
七、集成flask-migrate
"""

from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import create_app
from info.models import *

app = create_app("develop")

# 六、集成flask-script
manager = Manager(app)

# 七、集成flask-migrate, 在flask中对数据库进行迁移
Migrate(app=app, db=db)
manager.add_command("db", MigrateCommand)


# -n 命令参数简写 --username命令参数全称 dest = "要传的参数"
@manager.option("-n", "--username", dest="username")
@manager.option("-p", "--password", dest="password")
@manager.option("-m", "--mobile", dest="mobile")
def createsuperuser(username, password, mobile):
    """创建一个创建管理员的命令"""
    if not all([username, password, mobile]):
        print("参数不全")

    user = User()
    user.nick_name = username
    user.password = password
    user.mobile = mobile
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))

    print("创建管理员成功")


if __name__ == '__main__':
    manager.run()
