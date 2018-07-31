# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午3:09
@Software: PyCharm
@File    : gongxinbu.py
'''


import logging
import scrapy
import datetime
import time
import json
import requests

from lxml import etree
from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial
from common.common import clear


class jiangsu(scrapy.Spider):
    name = 'gongxinbu'
    header = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWe'
                            'bKit/537.36(KHTML, like Gecko) Chrome/6'
                            '3.0.3239.132 Safari/537.36'}
    area = 'gongxinbu'
    origin = "gongxinbu"
    keys = ['工业互联网','工业App']

    def start_requests(self):
        for key in self.keys:
            yield scrapy.FormRequest(
                    url="http://searchweb.miit.gov.cn/search/search",
                    headers=self.header,
                    formdata={"urls":"http://www.miit.gov.cn/","sortKey":"showTime","sortFlag":"-1","sortType":"1","indexDB":"css","pageSize":"10","pageNow":"1","fullText":key},
                    callback=lambda response, key=key: self.get_page(response,key)
                )

    def get_page(self, response, key):
        data = json.loads(response.body)
        page = int(data["total"])/int(data["pageSize"])
        page = int(page+1) if page>int(page) else int(page)
        for p in range(1,page+1):
            yield scrapy.FormRequest(
                url="http://searchweb.miit.gov.cn/search/search",
                headers=self.header,
                formdata={"urls": "http://www.miit.gov.cn/", "sortKey": "showTime", "sortFlag": "-1", "sortType": "1",
                          "indexDB": "css", "pageSize": "10", "pageNow": str(p), "name": key, "num": "10",
                          "rangeKey": "showTime"},
                callback=lambda response, key=key: self.get_url(response,key)
            )

    def get_url(self,response, key):
        data = json.loads(response.body)
        data = data["array"]
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        for item in data:
            url_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"url": item["url"]}
            )
            title = item["name"].replace("<font color='red'>","").replace("</font>","").replace("<nobr>","").replace("</nobr>","")
            if key == "工业App" and ("工业" not in title or ("App" not in title and "APP" not in title and "app" not in title)):
                logging.info("-----------工业App not in article------------")
                continue
            title_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"title": title}
            )
            if title_exits:
                logging.info("-----------already exits------------")
                continue
            s["url"] = item["url"]
            s['title'] = title
            s['area'] = self.area
            date = datetime.datetime.strptime(item["showTime"], "%Y-%m-%d")
            s['time'] = time.mktime(date.timetuple())
            s['origin'] = self.origin
            s['nature'] = "None"
            s['keyword'] = key
            try:
                db_agent.add(
                    kwargs=dict(s),
                    orm_model=Industrial
                )
                logging.info("-----------add success------------")
                add = True
            except:
                logging.info("-----------add error------------")
                add = False

            # if add:
            #     res = requests.get(
            #         url=item["url"],
            #         headers=self.header,
            #     )
            #     res = res.content
            #     selector = etree.HTML(res)
            #     data = selector.xpath('//div[@class="content"]//text()')
            #     if len(data) == 0:
            #         data = selector.xpath('//div[@id="con_con"]//text()')
            #     data = "".join(list(map(clear,data)))
            #     with open('./export/gongxinbu/{filename}.html'.format(filename=s['title']), 'w',
            #               encoding=("utf8")) as f:
            #         f.write(str(data))
            yield s

