# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午1:50
@Software: PyCharm
@File    : zhejiang.py.py
'''


import logging
import time
import scrapy
import requests
import datetime

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class shanghai(scrapy.Spider):
    name = 'zhejiangapp'
    header = {'Cache-Control': 'max-age=0','Origin': 'http://www.sheitc.gov.cn','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer': 'http://www.sheitc.gov.cn/zxgkxx/index.htm','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8','Cookie': '_sheitc=jinasgKzas; _gscu_1260451812=302449692ovey868; _gscbrs_1260451812=1; gwideal_date=day; gwdshare_firstime=1530244999495; JSESSIONID=D383BDE1FE6128262786C9E91058B1D2; _gscs_1260451812=t30258567798d7510|pv:12'}
    area = "zhejiang"
    origin = "zhejiang"
    url = 'http://www.zjjxw.gov.cn/jrobot/search.do?webid=1585&pg=12&p={p}&tpl=&category=&q=%E5%B7%A5%E4%B8%9AApp&pq=%E5%B7%A5%E4%B8%9AApp&oq=&eq=&doctype=&pos=&od=0&date=&date='
    key = "工业App"

    def start_requests(self):
        yield scrapy.Request(
            url=self.url.format(p="1"),
            headers=self.header,
            callback=self.get_page
        )

    def get_page(self,response):
        page = int(response.xpath('//div[@id="jsearch-info-box"]/@data-total').extract()[0])/12
        if page>int(page):
            p = int(page+1)
        else:
            p = int(page)
        for x in range(1,p+1):
            yield scrapy.Request(
                dont_filter=True,
                url=self.url.format(p=x),
                headers=self.header,
                callback=self.get_url
            )


    def get_url(self,response):
        db_agent = DatabaseAgent()
        urls = response.xpath('//div[@class="jsearch-result-title"]/a[1]/@href').extract()
        for url in urls:
            url_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"url": 'http://www.zjjxw.gov.cn/'+url}
            )
            if url_exits:
                logging.info("-----------already exits------------")
                continue
            yield scrapy.Request(
                url='http://www.zjjxw.gov.cn/'+url,
                headers=self.header,
                callback=self.get_data
            )

    def get_data(self,response):
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        # s['data'] = response.body.decode("GBK").encode("utf8")
        s['title'] = response.xpath('//title/text()').extract()[0]
        if "工业" not in s['title'] and "App" not in s['title'] and "APP" not in s['title'] and "app" not in s[
            'title']:
            yield s
        else:
            s['url'] = response.url
            s['time'] = response.xpath('//meta[@name="PubDate"]/@content').extract()[0]
            date = datetime.datetime.strptime(s['time'], "%Y-%m-%d %H:%M")
            s['time'] = time.mktime(date.timetuple())
            s['nature'] = "None"
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


