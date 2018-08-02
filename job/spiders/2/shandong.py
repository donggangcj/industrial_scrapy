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
import requests
import json

from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial


class shandong(scrapy.Spider):
    name = 'shandong'
    header = {'Cache-Control': 'max-age=0', 'Origin': 'http://www.aheic.gov.cn', 'Upgrade-Insecure-Requests': '1',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
              'Referer': 'http://www.sheitc.gov.cn/zxgkxx/index.htm', 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
              'Cookie': '_sheitc=jinasgKzas; _gscu_1260451812=302449692ovey868; _gscbrs_1260451812=1; gwideal_date=day; gwdshare_firstime=1530244999495; _gscs_1260451812=t30258567798d7510|pv:12'}
    area = "shandong"
    origin = "shandong"
    url = 'http://www.sdeic.gov.cn/gentleCMS/f_articlesearch/getSearchArticleListForNameorContent.do'
    keys = ['工业互联网','工业App']

    def start_requests(self):
        for key in self.keys:
            res_page = requests.post(
                url=self.url,
                headers=self.header,
                data={"siteid": "934369d9-7c20-45e0-a919-08ed9d557a1d","pageIndex":"1","pageSize":"15","name":key,"sitePubUrl":"/","number":"","time":"","channelid":""},
            )
            page = int(json.loads(res_page.content)['result']['pagecount'])
            for p in range(1,page+1):
                res = requests.post(
                    url=self.url,
                    headers=self.header,
                    data={"siteid": "934369d9-7c20-45e0-a919-08ed9d557a1d", "pageIndex": p, "pageSize": "15",
                          "name": key, "sitePubUrl": "/", "number": "", "time": "", "channelid": ""},
                )
                try:
                    json.loads(res.content)['result']['articleList']
                except:
                    continue
                for data in json.loads(res.content)['result']['articleList']:
                    data['PUBURL'] = 'http://www.sdeic.gov.cn' + data['PUBURL']
                    yield scrapy.Request(
                        url=data['PUBURL'],
                        headers=self.header,
                        callback=lambda response,key=key,data=data: self.save_data(response,key,data)
                    )

    def save_data(self,response,key,data):
        # article = response.xpath()
        db_agent = DatabaseAgent()
        s = IndustrialItem()
        s['title'] = data['NAME']
        if key == "工业App" and ("工业" not in s['title'] or ("App" not in s['title'] and "APP" not in s[
            'title'] and "app" not in s['title'])):
            pass
        else:
            pattern = re.compile(r'发布时间：(.*?)&nbsp;')
            date = pattern.search(response.body.decode("utf8")).group(1)
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
            s['time'] = int(time.mktime(date.timetuple()))
            s['area'] = self.area
            s['origin'] = self.origin
            s['keyword'] = key
            s['url'] = data['PUBURL']
            s['nature'] = data['CHANNELNAME']
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
