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

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class jiangsu(scrapy.Spider):
    name = 'gongxinbuapp'
    header = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWe'
                            'bKit/537.36(KHTML, like Gecko) Chrome/6'
                            '3.0.3239.132 Safari/537.36'}
    area = 'gongxinbu'
    origin = "gongxinbu"
    key = "工业App"

    def start_requests(self):
        yield scrapy.FormRequest(
            url="http://searchweb.miit.gov.cn/search/search",
            headers=self.header,
            formdata={"urls":"http://www.miit.gov.cn/","sortKey":"showTime","sortFlag":"-1","sortType":"1","indexDB":"css","pageSize":"10","pageNow":"1","name":"工业App","num":"10","rangeKey":"showTime"},
            callback=self.get_page
        )

    def get_page(self, response):
        data = json.loads(response.body)
        page = int(data["total"])/int(data["pageSize"])
        page = int(page+1) if page>int(page) else int(page)
        for p in range(1,page+1):
            yield scrapy.FormRequest(
                url="http://searchweb.miit.gov.cn/search/search",
                headers=self.header,
                formdata={"urls": "http://www.miit.gov.cn/", "sortKey": "showTime", "sortFlag": "-1", "sortType": "1",
                          "indexDB": "css", "pageSize": "10", "pageNow": str(p), "name": "工业App", "num": "10",
                          "rangeKey": "showTime"},
                callback=self.get_url
            )

    def get_url(self,response):
        data = json.loads(response.body)
        data = data["array"]
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        for item in data:
            url_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"url": item["url"]}
            )
            if url_exits:
                logging.info("-----------already exits------------")
                continue
            title = item["name"].replace("<font color='red'>","").replace("</font>","").replace("<nobr>","").replace("</nobr>","")
            title_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"title": title}
            )
            if title_exits:
                logging.info("-----------already exits------------")
                continue

            s['title'] = title
            if "工业" not in s['title'] and "App" not in s['title'] and "APP" not in s['title'] and "app" not in s[
                'title']:
                yield s
            else:
                s["url"] = item["url"]
                s['area'] = self.area
                date = datetime.datetime.strptime(item["showTime"], "%Y-%m-%d")
                s['time'] = time.mktime(date.timetuple())
                s['origin'] = self.origin
                s['nature'] = "None"
                s['keyword'] = self.key
                db_agent.add(
                    kwargs=dict(s),
                    orm_model=Industrial
                )
                try:
                    db_agent.add(
                        kwargs=dict(s),
                        orm_model=Industrial
                    )
                    logging.info("-----------add success------------")
                except:
                    logging.info("-----------add error------------")
                    pass
                yield s

