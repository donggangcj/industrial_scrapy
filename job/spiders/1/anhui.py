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
from common.common import clear


class shanghai(scrapy.Spider):
    name = 'anhui'
    header = {'Cache-Control': 'max-age=0','Origin': 'http://www.aheic.gov.cn','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer': 'http://www.sheitc.gov.cn/zxgkxx/index.htm','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8','Cookie': '_sheitc=jinasgKzas; _gscu_1260451812=302449692ovey868; _gscbrs_1260451812=1; gwideal_date=day; gwdshare_firstime=1530244999495; _gscs_1260451812=t30258567798d7510|pv:12'}
    area = "anhui"
    origin = "anhui"
    url = 'http://www.aheic.gov.cn/search.jsp'
    key = '工业互联网'

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url,
            headers=self.header,
            formdata={"keyValue": "工业互联网".encode("GB2312"),"keyName":"strMasTitle"},
            callback=self.get_page
        )

    def get_page(self,response):
        page = response.xpath('//span[@class="disabled"]/text()').extract()[-1]
        page = int(page.replace('/',''))
        for x in range(1,page+1):
            yield scrapy.FormRequest(
                url=self.url,
                headers=self.header,
                formdata={"keyValue": "工业互联网".encode("GB2312"), "keyName": "strMasTitle","PageSizeIndex":str(x)},
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
        s['keyword'] = self.key
        s['title'] = s['title'].replace("安徽省经济和信息化委员会 ","")
        try:
            db_agent.add(
                kwargs=dict(s),
                orm_model=Industrial
            )
            res = True
            logging.info("-----------add success------------")
        except Exception as e:
            res = False
            logging.info(e)
            logging.info("-----------add error------------")
            pass
        # if res:
        #     data = "".join(list(map(clear,response.xpath('//div[@id="zoom"]//text()').extract())))
        #     with open('./export/anhui/{filename}.html'.format(filename=s['title']), 'w', encoding=("utf8")) as f:
        #         f.write(str(data))
        yield s