# __coding:utf-8__
'''
@Author  : Sun
@Time    :  下午3:59
@Software: PyCharm
@File    : chanyelianmeng.py
'''


import logging
import requests
import time
import scrapy
import datetime

from lxml import etree
from common.dbtools import DatabaseAgent
from job.items import IndustrialItem
from job.models.industrial import Industrial
from common.common import clear


class shanghai(scrapy.Spider):
    name = 'chanyelianmeng'
    header = {'Cache-Control': 'max-age=0','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Referer': 'http://www.sheitc.gov.cn/zxgkxx/index.htm','Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8','Cookie': '_sheitc=jinasgKzas; _gscu_1260451812=302449692ovey868; _gscbrs_1260451812=1; gwideal_date=day; gwdshare_firstime=1530244999495; JSESSIONID=D383BDE1FE6128262786C9E91058B1D2; _gscs_1260451812=t30258567798d7510|pv:12'}
    area = "chanyelianmeng"
    origin = "chanyelianmeng"
    url = 'http://www.aii-alliance.org/index.php?m=content&c=search&a=search&page={p}'
    keys = ['工业互联网','工业App']

    def start_requests(self):
        for key in self.keys:
            yield scrapy.FormRequest(
                url=self.url.format(p="1"),
                headers=self.header,
                formdata={"search": key},
                callback=lambda response, key=key: self.get_page(response,key)
            )

    def get_page(self,response, key):
        try:
            p = int(response.xpath('//div[@id="pages"]/a[last()-1]/text()').extract()[0])
        except:
            p = 1
        for x in range(1,p+1):
            yield scrapy.FormRequest(
                dont_filter=True,
                url=self.url.format(p=x),
                headers=self.header,
                formdata={"search": key},
                callback=lambda response, key=key: self.get_url(response,key)
            )


    def get_url(self,response, key):
        s = IndustrialItem()
        db_agent = DatabaseAgent()
        urls = response.xpath('//ul[@class="download_list"]/li/a/@href').extract()
        for url in urls:
            url_exits = db_agent.get(
                orm_model=Industrial,
                filter_kwargs={"url": url}
            )
            if url_exits:
                logging.info("-----------already exits------------")
                continue
            date = response.xpath('//a[@href="{url}"]/div/text()'.format(url=url)).extract()[0]
            date = date.replace(' ', '')
            date = datetime.datetime.strptime(date, "%Y.%m.%d")
            s['title'] = response.xpath('//a[@href="{url}"]/h2/text()'.format(url=url)).extract()[0]
            if key == "工业App" and ("工业" not in s['title'] or ("App" not in s['title'] and "APP" not in s[
                'title'] and "app" not in s['title'])):
                add = False
            else:
                s['time'] = time.mktime(date.timetuple())
                s['nature'] = "None"
                s['area'] = self.area
                s['origin'] = self.origin
                s['url'] = url
                s['keyword'] = key
                try:
                    db_agent.add(
                        kwargs=dict(s),
                        orm_model=Industrial
                    )
                    logging.info("-----------add success------------")
                    add = True
                except Exception as e:
                    logging.info(e)
                    logging.info("-----------add error------------")
                    add = False
            if add:
                res = requests.get(
                    url=url,
                    headers=self.header,
                )
                res = res.content
                selector = etree.HTML(res)
                data = "".join(list(map(clear,selector.xpath('//div[@class="inside_content_text"]//text()'))))
                with open('./export/chanyelianmeng/{filename}.html'.format(filename=s['title']), 'w',
                          encoding=("utf8")) as f:
                    f.write(str(data))
            yield s




