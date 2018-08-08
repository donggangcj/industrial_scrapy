# -*- coding: utf-8 -*-

import logging
import scrapy
import datetime
import time
import re

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial
from common.common import is_exits,clear


class beijing(scrapy.Spider):
    name = 'beijing'
    header = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWe'
                            'bKit/537.36(KHTML, like Gecko) Chrome/6'
                            '3.0.3239.132 Safari/537.36',
              "Content-Type": 'application/x-www-form-urlencoded'}
    area = 'beijing'
    origin = "beijing"
    keys = ['工业互联网','工业App']
    url = 'http://jxw.beijing.gov.cn:8080/oasearch/front/search.do'

    def start_requests(self):
        for key in self.keys:
            yield scrapy.FormRequest(
                url=self.url,
                headers=self.header,
                formdata={"pageNo":"1","orderField":"","orderType":"","query":key},
                callback=lambda response,key=key: self.get_page(response,key)
            )

    def get_page(self, response, key):
        pattern = re.compile(r'共(\d+)页')
        page = int(pattern.search(response.body.decode('utf8')).group(1))
        for p in range(1,page+1):
            yield scrapy.FormRequest(
                dont_filter=True,
                url=self.url,
                headers=self.header,
                formdata={"pageNo":str(p),"orderField":"","orderType":"","query":key},
                callback=lambda response,key=key: self.get_data(response,key)
            )


    def get_data(self,response, key):
        # a = response.body.decode('utf8')
        # print(a)
        # print('-------------')
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        for index in range(1,21):
            print(index)
            s['url'] = response.xpath('//ul[last()]/li[{index}]/dl[@class="result_text"]/dt/a/@href'.format(index=index)).extract()
            s['title'] = response.xpath('//ul[last()]/li[{index}]/dl[@class="result_text"]/dt/a/i//text()'.format(index=index)).extract()
            s['title'] = ''.join(s['title'])
            if not is_exits(s["title"], s["url"]):
                continue
            s["time"] = clear(response.xpath('//ul[last()]/li[{index}]/dl[@class="result_text"]/dt/p/text()'.format(index=index)).extract()[0])
            s["time"] = datetime.datetime.strptime(s["time"], "%Y-%m-%d")
            s['time'] = int(time.mktime(s["time"].timetuple()))
            s['area'] = self.area
            s['origin'] = self.origin
            s['nature'] = ''
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
