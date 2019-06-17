from flask import current_app

from info import constants


class Paginate(object):
    """查询分页"""

    @classmethod
    def find_paginate(cls, user_attribute, page, order=False, obj=None):
        try:
            page = int(page)
        except Exception as e:
            current_app.logger.error(e)
            page = 1

        # 查看用户收藏的新闻
        news_list = []
        current_page = 1
        total_page = 1
        if order:
            try:
                paginate = user_attribute.order_by(obj.create_time.desc()).paginate(page,
                                                                                    constants.USER_COLLECTION_MAX_NEWS,
                                                                                    False)
                news_list = paginate.items
                current_page = paginate.page
                total_page = paginate.pages
            except Exception as e:
                current_app.logger.error(e)

            return news_list, current_page, total_page
        else:
            try:
                paginate = user_attribute.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
                news_list = paginate.items
                current_page = paginate.page
                total_page = paginate.pages
            except Exception as e:
                current_app.logger.error(e)

            return news_list, current_page, total_page
