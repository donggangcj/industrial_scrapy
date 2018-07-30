# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午3:10
@Software: PyCharm
@File    : shanghai_xinxigongkai.py
'''


# -*- coding: utf-8 -*-

import re
import time
import scrapy
import requests
import datetime
import logging

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class shanghai(scrapy.Spider):
    name = 'shanghai'
    header = {'Cache-Control': 'max-age=0','Origin': 'http://www.sheitc.gov.cn','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer': 'http://www.sheitc.gov.cn/zxgkxx/index.htm','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8','Cookie': '_sheitc=jinasgKzas; _gscu_1260451812=302449692ovey868; _gscbrs_1260451812=1; gwideal_date=day; gwdshare_firstime=1530244999495; JSESSIONID=D383BDE1FE6128262786C9E91058B1D2; _gscs_1260451812=t30258567798d7510|pv:12'}
    area = "shanghai"
    origin = "shanghaijingjihexinxihuaweiyuanhui"
    keys = ['工业互联网','工业App']

    def start_requests(self):
        url = 'http://www.sheitc.gov.cn/zxgkxx/index_{p}.htm'
        for key in self.keys:
            res = requests.post(
                url=url.format(p=""),
                headers=self.header,
                data={"searchKey":key.encode("GB2312")}
            )
            pattern = re.compile(r'共(\d+)条记录')
            page = int(pattern.search(res.content.decode('GBK')).group(1))/10
            p = int(page)+2 if page > int(page) else int(page)+2
            for x in range(1,p):
                yield scrapy.FormRequest(
                    url=url.format(p=x),
                    headers=self.header,
                    formdata={"searchKey": key.encode("GB2312")},
                    callback=lambda response,key=key: self.get_url(response,key)
                )



    def get_url(self,response, key):
        db_agent = DatabaseAgent()
        urls = response.xpath('//ul[@class="list clearfix"]/div[@class="li"]/p/a/@href').extract()
        for url in urls:
            url_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"url": url}
            )
            print(key)
            if url_exits:
                logging.info("-----------already exits------------")
                continue
            yield scrapy.Request(
                url=url,
                headers=self.header,
                callback=lambda response,key=key: self.parse(response,key)
            )

    def parse(self,response,key):
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        s['url'] = response.url
        s['title'] = response.xpath('//title/text()').extract()[0]
        s['title'] = "《上海市工业互联网创新发展专项支持实施细则》的通知"
        if key == "工业App" and ("工业" not in s['title'] or ("App" not in s['title'] and "APP" not in s[
            'title'] and "app" not in s['title'])):
            pass
        else:
            s['time'] = response.xpath('//meta[@name="PubDate"]/@content').extract()[0]
            date = datetime.datetime.strptime(s['time'], "%Y-%m-%d %H:%M")
            s['time'] = time.mktime(date.timetuple())
            s['nature'] = response.xpath('//meta[@name="ColumnKeywords"]/@content').extract()[0]
            s['area'] = self.area
            s['origin'] = self.origin
            s['keyword'] = key
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


