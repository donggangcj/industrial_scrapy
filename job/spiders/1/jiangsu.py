# -*- coding: utf-8 -*-

import logging
import scrapy
import datetime
import time

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class jiangsu(scrapy.Spider):
    name = 'jiangsu'
    header = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWe'
                            'bKit/537.36(KHTML, like Gecko) Chrome/6'
                            '3.0.3239.132 Safari/537.36'}
    area = 'jiangsu'
    origin = "jiangsu"
    keys = ['工业互联网','工业App']
    key_map = {"工业互联网": "%E5%B7%A5%E4%B8%9A%E4%BA%92%E8%81%94%E7%BD%91", "工业App": "%E5%B7%A5%E4%B8%9AApp"}

    def start_requests(self):
        for key in self.keys:
            yield scrapy.Request(
                url='http://www.jiangsu.gov.cn/jrobot/search.do?webid=23&analyzeType=1&pg=10&p={p}&tpl=2&category=&q={key}&pos=&od=&date=&date='.format(
                    p=1,key=self.key_map[key]),
                headers=self.header,
                callback=lambda response,key=key: self.get_page(response,key)
            )

    def get_page(self, response, key):
        page = response.xpath('//div[@id="jsearch-info-box"]/@data-total').extract()[0]
        page = int(page) / 10
        if page > int(page):
            p = int(page) + 1
        else:
            p = int(page)
        for x in range(1, p + 1):
            yield scrapy.Request(
                url='http://www.jiangsu.gov.cn/jrobot/search.do?webid=23&analyzeType=1&pg=10&p={p}&tpl=2&category=&q={key}&pos=&od=&date=&date='.format(
                    p=x, key=self.key_map[key]),
                headers=self.header,
                callback=lambda response,key=key: self.get_url(response,key)
            )


    def get_url(self,response, key):
        db_agent = DatabaseAgent()
        urls = response.xpath('//div[@class="jsearch-result-url"]/a/text()').extract()
        for url in urls:
            url_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"url": url}
            )
            if url_exits:
                logging.info("-----------already exits------------")
                continue
            yield scrapy.Request(
                url=url,
                headers=self.header,
                callback=lambda response,key=key: self.get_data(response,key)
            )

    def get_data(self,response, key):
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        s['url'] = response.url
        s['title'] = response.xpath('//title/text()').extract()[0]
        if key == "工业App" and ("工业" not in s['title'] or ("App" not in s['title'] and "APP" not in s[
            'title'] and "app" not in s['title'])):
            pass
        else:
            s['time'] = response.xpath('//meta[@name="PubDate"]/@content').extract()[0]
            date = datetime.datetime.strptime(s['time'], "%Y-%m-%d %H:%M")
            s['time'] = time.mktime(date.timetuple())
            s['nature'] = "None"
            s['area'] = self.area
            s['origin'] = self.origin
            s['keyword'] = key
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
