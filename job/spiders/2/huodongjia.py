# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午4:05
@Software: PyCharm
@File    : huodongjia.py
'''



import logging
import scrapy
import datetime
import time
import json

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class huodongjia(scrapy.Spider):
    name = 'huodongjia'
    area = 'huodongjia'
    origin = 'huodongjia'
    headers = {"X-Requested-With":"XMLHttpRequest",'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
    url = 'https://www.huodongjia.com/search/events/page-{p}/?keyword={key}'
    keys = ["工业互联网","工业物联网","物联网"]
    keymap = {"工业互联网":"%E5%B7%A5%E4%B8%9A%E4%BA%92%E8%81%94%E7%BD%91","工业物联网":"%E5%B7%A5%E4%B8%9A%E7%89%A9%E8%81%94%E7%BD%91","物联网":"%E7%89%A9%E8%81%94%E7%BD%91"}

    def start_requests(self):
        for key in self.keys:
            yield scrapy.Request(
                dont_filter=True,
                url=self.url.format(p=2,key=self.keymap[key]),
                headers=self.headers,
                callback=lambda response,key=key: self.get_page(response,key)
            )

    def get_page(self,response,key):
        page = json.loads(response.body)
        length = page['total_length']
        page = int(length/10)
        for p in range(page+1):
            yield scrapy.Request(
                url=self.url.format(p=p,key=self.keymap[key]),
                headers=self.headers,
                callback=lambda response,key=key: self.get_data(response,key)
            )

    def get_data(self,response,key):
        data = json.loads(response.body)
        s = IndustrialItem()
        db_agent = DatabaseAgent()
        for item in data['events']:
            s['title'] = item['event_name']
            s['url'] = 'https://www.huodongjia.com'+item['event_url']
            s['area'] = self.area
            s['keyword'] = "工业互联网活动"
            s['nature'] = "活动"
            s['origin'] = self.origin
            date = datetime.datetime.strptime(item['event_begin_time'], "%Y-%m-%d")
            s['time'] = int(time.mktime(date.timetuple()))
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






