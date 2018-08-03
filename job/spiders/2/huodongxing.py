# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午3:01
@Software: PyCharm
@File    : huodongxing.py
'''



import logging
import scrapy
import datetime
import time

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class huodongxing(scrapy.Spider):
    name = 'huodongxing'
    area = 'huodongxing'
    origin = 'huodongxing'
    url = 'http://www.huodongxing.com/search?ps=12&pi={p}&list=list&qs={key}&st=1,4&city=%E5%85%A8%E5%9B%BD'
    keys = ["工业互联网","工业物联网"]
    keymap = {"工业互联网":"%E5%B7%A5%E4%B8%9A%E4%BA%92%E8%81%94%E7%BD%91","工业物联网":"%E5%B7%A5%E4%B8%9A%E7%89%A9%E8%81%94%E7%BD%91"}

    def start_requests(self):
        for key in self.keys:
            yield scrapy.Request(
                url=self.url.format(key=self.keymap[key],p=0),
                callback=lambda response,key=key: self.get_page(response,key)
            )

    def get_page(self,response,key):
        page = int(response.xpath('//div[@class="search-tab-content hdx-new-content--active"]/p/a[@class="main-color"]/text()').extract()[1])/12+1
        for p in range(1,int(page+1)):
            yield scrapy.Request(
                url=self.url.format(key=self.keymap[key],p=p),
                callback=lambda response,key=key: self.get_data(response,key)
            )

    def get_data(self,response,key):
        s = IndustrialItem()
        db_agent = DatabaseAgent()
        for item in range(1,13):
            s['title'] = response.xpath('//div[@class="search-tab-content-list"]/div[@class="search-tab-content-item flex"][{x}]/a/img/@title'.format(x=item)).extract()[0]
            s['url'] = response.xpath('//div[@class="search-tab-content-list"]/div[@class="search-tab-content-item flex"][{x}]/a[1]/@href'.format(x=item)).extract()[0]
            s['url'] = 'http://www.huodongxing.com' + s['url']
            s['area'] = self.area
            s['keyword'] = "工业互联网活动"
            s['nature'] = "活动"
            s['origin'] = self.origin
            s['time'] = response.xpath('//div[@class="search-tab-content-list"]/div[@class="search-tab-content-item flex"][{x}]/div[@class="search-tab-content-item-right"]/p[@class="item-data flex"]/text()'.format(x=item)).extract()[0].split('-')[0]
            date = datetime.datetime.strptime(s['time'], "%Y.%m.%d")
            s['time'] = time.mktime(date.timetuple())
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






