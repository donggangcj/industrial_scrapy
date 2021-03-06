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


class anhui(scrapy.Spider):
    name = 'anhui'
    header = {'Cache-Control': 'max-age=0','Origin': 'http://www.aheic.gov.cn','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer': 'http://www.sheitc.gov.cn/zxgkxx/index.htm','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8','Cookie': '_sheitc=jinasgKzas; _gscu_1260451812=302449692ovey868; _gscbrs_1260451812=1; gwideal_date=day; gwdshare_firstime=1530244999495; _gscs_1260451812=t30258567798d7510|pv:12'}
    area = "anhui"
    origin = "anhui"
    url = 'http://www.aheic.gov.cn/search.jsp'
    keys = ['工业互联网','工业App']

    def start_requests(self):
        for key in self.keys:
            yield scrapy.FormRequest(
                url=self.url,
                headers=self.header,
                formdata={"keyValue": key.encode("GB2312"),"keyName":"strMasTitle"},
                callback=lambda response,key=key: self.get_page(response,key)
            )

    def get_page(self,response,key):
        page = response.xpath('//span[@class="disabled"]/text()').extract()[-1]
        page = int(page.replace('/',''))
        for x in range(1,page+1):
            yield scrapy.FormRequest(
                url=self.url,
                headers=self.header,
                formdata={"keyValue": key.encode("GB2312"), "keyName": "strMasTitle","PageSizeIndex":str(x)},
                callback=lambda response,key=key: self.get_url(response,key)
            )


    def get_url(self,response,key):
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
                callback=lambda response,key=key: self.get_data(response,key)
            )

    def get_data(self,response,key):
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
        s['keyword'] = key
        s['title'] = s['title'].replace("安徽省经济和信息化委员会 ","")
        try:
            if key=="工业App" and ("工业" not in s['title'] or ("App" not in s['title'] and "APP" not in s['title'] and "app" not in s[
                'title'])):
                pass
            else:
                db_agent.add(
                    kwargs=dict(s),
                    orm_model=Industrial
                )
                logging.info("-----------add success------------")
                # data = "".join(list(map(clear,response.xpath('//div[@id="zoom"]//text()').extract())))
                # with open('./export/anhui/{filename}.html'.format(filename=s['title']), 'w', encoding=("utf8")) as f:
                #     f.write(str(data))
        except Exception as e:
            logging.info(e)
            logging.info("-----------add error------------")
            pass
        yield s