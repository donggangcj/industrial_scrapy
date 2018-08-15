# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午2:03
@Software: PyCharm
@File    : guangdong.py
'''

import logging
import scrapy
import datetime
import time
import re

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial
from common.common import is_exits,clear


class guangdong(scrapy.Spider):
    name = 'guangdong'
    header = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWe'
                            'bKit/537.36(KHTML, like Gecko) Chrome/6'
                            '3.0.3239.132 Safari/537.36',
              "Content-Type": 'application/x-www-form-urlencoded'}
    area = 'guangdong'
    origin = "guangdong"
    keys = ['工业互联网','工业App']
    keymap = {"工业互联网": "%E5%B7%A5%E4%B8%9A%E4%BA%92%E8%81%94%E7%BD%91", "工业App": "%E5%B7%A5%E4%B8%9AApp"}
    url = 'http://61.144.19.76:8080/was5/web/search?page={p}&channelid=249060&searchword={key}&keyword={key}&perpage=10&outlinepage=5'

    def start_requests(self):
        for key in self.keys:
            yield scrapy.Request(
                url=self.url.format(p=1,key=self.keymap[key]),
                headers=self.header,
                callback=lambda response,key=key: self.get_page(response,key)
            )

    def get_page(self, response, key):
        pattern = re.compile(r'总页数：(\d+)</div>')
        page = int(pattern.search(response.body.decode('utf8')).group(1))
        print(page)
        for p in range(1,page+1):
            yield scrapy.Request(
                dont_filter=True,
                url=self.url.format(p=1,key=self.keymap[key]),
                headers=self.header,
                callback=lambda response,key=key: self.get_data(response,key)
            )


    def get_data(self,response, key):

        db_agent = DatabaseAgent()
        s = IndustrialItem()
        for index in range(1,11):
            s['url'] = response.xpath('//div[@class="Main"]/dl[{index}]/dt/a/@href'.format(index=index)).extract()
            s['title'] = response.xpath('//div[@class="Main"]/dl[{index}]/dt/a//text()'.format(index=index)).extract()
            s['title'] = ''.join(s['title'])
            if not is_exits(s["title"], s["url"]):
                continue
            s['area'] = self.area
            s['origin'] = self.origin
            s['nature'] = ''
            s['keyword'] = key
            s['time'] = response.xpath('//div[@class="Main"]/dl[{index}]/dd[last()]/span[@style="color:#666"]/text()'.format(index=index)).extract()[0]
            s["time"] = datetime.datetime.strptime(s["time"], "%Y.%m.%d %H:%M:%S")
            s['time'] = int(time.mktime(s["time"].timetuple()))
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
