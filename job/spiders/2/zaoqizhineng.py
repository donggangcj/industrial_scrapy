# __coding:utf-8__
'''
@Author  : Sun
@Time    :  上午10:55
@Software: PyCharm
@File    : zaoqizhineng.py
'''


import logging
import scrapy
import datetime
import time
import requests
import json
from lxml import etree
from common.common import is_exits
from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class zaoqizhineng(scrapy.Spider):
    name = 'zaoqizhineng'
    area = 'zaoqizhineng'
    url = 'http://dy.163.com/v2/article/list.do?pageNo={p}&wemediaId=W6693795521914779026&size=10'

    def start_requests(self):
        for x in range(0,22):
            yield scrapy.Request(
                url=self.url.format(p=x),
                callback=self.get_data
            )

    def get_data(self,response):
        s = IndustrialItem()
        db_agent = DatabaseAgent()
        res = response
        res = json.loads(res.text)
        if res['data']!=None:
            for data in res['data']['list']:
                s["title"] = data["title"]
                # if "工业互联网" not in s['title']:
                #     continue
                s["area"] = self.area
                s["nature"] = "新闻"
                s["origin"] = "zaoqizhineng"
                s["time"] = datetime.datetime.strptime(data['ptime'], "%Y-%m-%d %H:%M:%S")
                s["time"] = int(time.mktime(s["time"].timetuple()))
                s["url"] = 'http://dy.163.com/v2/article/detail/{docid}.html'.format(docid=data['docid'])
                s['keyword'] = "工业互联网活动"
                try:
                    db_agent.add(
                        kwargs=dict(s),
                        orm_model=Industrial
                    )
                    logging.info("-----------add success------------")
                except Exception as e:
                    logging.info(e)
                    logging.info("-----------add error------------")
                    pass
            yield s






