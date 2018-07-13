# __coding:utf-8__
'''
@Author  : Sun
@Time    :  上午11:06
@Software: PyCharm
@File    : index.py
'''


import re
from common.dbtools import DatabaseAgent, sqlalchemy_session
from common.common import to_json
from flask import request, Blueprint
from job.models.industrial import Industrial

api = Blueprint('api', __name__)

@api.route("/latest", methods=['get'])
def get_latest():
    res = []
    with sqlalchemy_session() as session:
        latest_new = session.query(Industrial).order_by("time").limit(10).all()
        for new in latest_new:
            res.append({"id":new.id,"title":new.title,"time":new.time,"url":new.url,"area":new.area,"nature":new.nature})
        return to_json(200, res)

@api.route("/news", methods=['post','get'])
def get_news():
    res = []
    item = {}
    data = request.json
    time = data.get("time",0)
    if time!=0:
        del data["time"]
    with sqlalchemy_session() as session:
        if data:
            print(1)
            news = session.query(Industrial).filter(Industrial.time >= time).filter_by(**data).order_by("time").all()
        else:
            print(2)
            news = session.query(Industrial).filter(Industrial.time >= time).order_by("time").all()
        for new in news:
            res.append({"id":new.id,"title":new.title,"time":new.time,"url":new.url,"area":new.area,"nature":new.nature})
        return to_json(200, res)