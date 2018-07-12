# -*- coding: utf-8 -*-

import re

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

    def start_requests(self):
        yield scrapy.Request(
            url='http://www.jiangsu.gov.cn/jrobot/search.do?webid=23&analyzeType=1&pg=10&p={p}&tpl=2&category=&q=%E5%B7%A5%E4%B8%9A%E4%BA%92%E8%81%94%E7%BD%91&pos=&od=&date=&date='.format(
                p=1),
            headers=self.header,
            callback=self.get_page
        )

    def get_page(self, response):
        page = response.xpath('//div[@id="jsearch-info-box"]/@data-total').extract()[0]
        page = int(page) / 10
        if page > int(page):
            p = int(page) + 1
        else:
            p = int(page)
        for x in range(1, p + 1):
            yield scrapy.Request(
                url='http://www.jiangsu.gov.cn/jrobot/search.do?webid=23&analyzeType=1&pg=10&p={p}&tpl=2&category=&q=%E5%B7%A5%E4%B8%9A%E4%BA%92%E8%81%94%E7%BD%91&pos=&od=&date=&date='.format(
                    p=x),
                headers=self.header,
                callback=self.get_url
            )


    def get_url(self,response):
        db_agent = DatabaseAgent()
        urls = response.xpath('//div[@class="jsearch-result-url"]/a/text()').extract()
        for url in urls:
            url_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"url": url}
            )
            if url_exits:
                print("-----------already exits------------")
                continue
            yield scrapy.Request(
                url=url,
                headers=self.header,
                callback=self.get_data
            )

    def get_data(self,response):
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        # s['data'] = response.body.decode("utf-8")
        s['url'] = response.url
        s['title'] = response.xpath('//title/text()').extract()[0]
        s['time'] = response.xpath('//meta[@name="PubDate"]/@content').extract()[0]
        date = datetime.datetime.strptime(s['time'], "%Y-%m-%d %H:%M")
        s['time'] = time.mktime(date.timetuple())
        s['nature'] = "None"
        s['area'] = self.area
        s['origin'] = self.origin
        try:
            db_agent.add(
                kwargs=dict(s),
                orm_model=Industrial
            )
            print("-----------add success------------")
        except:
            print("-----------add error------------")
            pass
        yield s
