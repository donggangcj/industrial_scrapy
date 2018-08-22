# __coding:utf-8__
'''
@Author  : Sun
@Time    :  上午10:40
@Software: PyCharm
@File    : souhu.py
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


class souhu(scrapy.Spider):
    name = 'souhu'
    header = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWe'
                            'bKit/537.36(KHTML, like Gecko) Chrome/6'
                            '3.0.3239.132 Safari/537.36'}
    area = 'souhu'
    keys = ["isesol","富士康beacon","用友工业互联网","根云","航天云网",'工业互联网','工业App']

    def start_requests(self):
        s = IndustrialItem()
        db_agent = DatabaseAgent()
        for key in self.keys:
            for x in range(0,180,10):
                res = requests.post(
                    url="http://search.sohu.com/outer/search/news",
                    headers=self.header,
                    data={"keyword":key,"size":"10","from":str(x),"city":"上海市","SUV":"1802211642505755","terminalType":"pc","source":"direct","queryType":"edit"}
                )
                res = json.loads(res.content.decode("utf8"))
                if res.get("data",None) == None:
                    break
                for new in res["data"]["news"]:
                    if not is_exits(new["title"],new["url"]):
                        continue
                    s["title"] = new["title"]
                    if key == "工业App" and ("工业" not in s['title'] or "app" not in s['title'].lower ):
                        continue
                    if key in ["isesol","beacon","用友工业互联网","根云","航天云网","工业App"] and (key.lower() not in s['title'].lower() ):
                        continue
                    s["url"] = new["url"]
                    s["area"] = self.area
                    s["origin"] = new["authorName"]
                    s["nature"] = None
                    try:
                        s["time"] = self.get_time(new["url"])
                    except:
                        continue
                    s['keyword'] = key
                    print(s)
                    try:
                        db_agent.add(
                            kwargs=dict(s),
                            orm_model=Industrial
                        )
                        logging.info("-----------add success------------")
                    except:
                        logging.info("-----------add error------------")
                        pass
                # yield s

    def get_time(self,url):
        res = requests.get(
            url=url,
            headers=self.header,
        )
        res = res.content
        selector = etree.HTML(res)
        date = selector.xpath('//meta[@itemprop="datePublished"]/@content')[0]
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        t = time.mktime(date.timetuple())
        return t
