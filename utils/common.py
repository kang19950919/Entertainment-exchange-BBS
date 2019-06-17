import functools

from flask import session, current_app, g


def do_index_class(index):
    if index == 1:
        return "first"
    if index == 2:
        return "second"
    if index == 3:
        return "third"
    return ""


# def user_login():
#     user_id = session.get("user_id")
#     user = None
#     if user_id:
#         try:
#             # 会出现循环导入所以在这里导入
#             from info.models import User
#             user = User.query.get(user_id)
#         except Exception as e:
#             current_app.logger.error(e)
#     return user


def user_login(func):
    # 必须加这个装饰器不然所有用user_login装饰器的函数都会用一个名字从而产生冲突
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                # 会出现循环导入所以在这里导入
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return func(*args, **kwargs)
    return wrapper


def admin_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        admin_id = session.get("admin_id")
        admin_user = None
        if admin_id:
            try:
                from info.models import User
                admin_user = User.query.get(admin_id)
            except Exception as e:
                current_app.logger.error(e)
        g.admin_user = admin_user
        return func(*args, **kwargs)
    return wrapper



