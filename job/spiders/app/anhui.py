# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午5:55
@Software: PyCharm
@File    : anhui.py
'''


import re
import time
import scrapy
import datetime
import logging

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class shanghai(scrapy.Spider):
    name = 'anhuiapp'
    header = {'Cache-Control': 'max-age=0','Origin': 'http://www.aheic.gov.cn','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer': 'http://www.sheitc.gov.cn/zxgkxx/index.htm','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8','Cookie': '_sheitc=jinasgKzas; _gscu_1260451812=302449692ovey868; _gscbrs_1260451812=1; gwideal_date=day; gwdshare_firstime=1530244999495; _gscs_1260451812=t30258567798d7510|pv:12'}
    area = "anhui"
    origin = "anhui"
    url = 'http://www.aheic.gov.cn/search.jsp'
    key = "工业App"

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url,
            headers=self.header,
            formdata={"keyValue": "工业App".encode("GB2312"),"keyName":"strMasTitle"},
            callback=self.get_page
        )

    def get_page(self,response):
        page = response.xpath('//span[@class="disabled"]/text()').extract()[-1]
        page = int(page.replace('/',''))
        for x in range(1,page+1):
            yield scrapy.FormRequest(
                url=self.url,
                headers=self.header,
                formdata={"keyValue": "工业App".encode("GB2312"), "keyName": "strMasTitle","PageSizeIndex":str(x)},
                callback=self.get_url
            )


    def get_url(self,response):
        db_agent = DatabaseAgent()
        urls = response.xpath('//div[@class="nest"]/p/a/@href').extract()
        for url in urls:
            url = 'http://www.aheic.gov.cn/'+url
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
                callback=self.get_data
            )

    def get_data(self,response):
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        # s['data'] = response.body.decode("GBK").encode("utf8")
        s['url'] = response.url
        s['title'] = response.xpath('//title/text()').extract()[0]
        s['time'] = response.xpath('//h5/text()').extract()[0]
        pattern = re.compile(r'.*(\d\d\d\d-\d\d-\d\d)')
        s['time'] = pattern.match(s['time']).group(1)
        date = datetime.datetime.strptime(s['time'], "%Y-%m-%d")
        s['time'] = time.mktime(date.timetuple())
        s['nature'] = response.xpath('//span[@class="where"]/a[last()]/text()').extract()[0]
        s['area'] = self.area
        s['origin'] = self.origin
        s['key'] = self.key
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

