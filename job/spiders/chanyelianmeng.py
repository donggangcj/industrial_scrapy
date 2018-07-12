# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午3:59
@Software: PyCharm
@File    : chanyelianmeng.py
'''


import re
import time
import scrapy
import requests
import datetime

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class shanghai(scrapy.Spider):
    name = 'chanyelianmeng'
    header = {'Cache-Control': 'max-age=0','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer': 'http://www.sheitc.gov.cn/zxgkxx/index.htm','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8','Cookie': '_sheitc=jinasgKzas; _gscu_1260451812=302449692ovey868; _gscbrs_1260451812=1; gwideal_date=day; gwdshare_firstime=1530244999495; JSESSIONID=D383BDE1FE6128262786C9E91058B1D2; _gscs_1260451812=t30258567798d7510|pv:12'}
    area = "chanyelianmeng"
    origin = "chanyelianmeng"
    url = 'http://www.aii-alliance.org/index.php?m=content&c=search&a=search&page={p}'

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url.format(p="1"),
            headers=self.header,
            formdata={"search": "工业互联网"},
            callback=self.get_page
        )

    def get_page(self,response):
        p = int(response.xpath('//div[@id="pages"]/a[last()-1]/text()').extract()[0])
        for x in range(1,p+1):
            yield scrapy.Request(
                dont_filter=True,
                url=self.url.format(p=x),
                headers=self.header,
                callback=self.get_url
            )


    def get_url(self,response):
        s = IndustrialItem()
        db_agent = DatabaseAgent()
        urls = response.xpath('//ul[@class="download_list"]/li/a/@href').extract()
        print(urls)
        for url in urls:
            url_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"url": url}
            )
            if url_exits:
                print("-----------already exits------------")
                continue
            date = response.xpath('//a[@href="{url}"]/div/text()'.format(url=url)).extract()[0]
            date = date.replace(' ', '')
            date = datetime.datetime.strptime(date, "%Y.%m.%d")
            s['title'] = response.xpath('//a[@href="{url}"]/h2/text()'.format(url=url)).extract()[0]
            s['time'] = time.mktime(date.timetuple())
            s['nature'] = "None"
            s['area'] = self.area
            s['origin'] = self.origin
            s['url'] = url
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



