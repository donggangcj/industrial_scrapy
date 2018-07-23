# # -*- coding: utf-8 -*-
#
# import re
#
# import scrapy
# # import requests
# import json
#
# from common.dbtools import DatabaseAgent
# from job.items import IndustrialItem
#
#
# class gongxinbu(scrapy.Spider):
#     name = 'gongxinbu'
#     header = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWe'
#                             'bKit/537.36(KHTML, like Gecko) Chrome/6'
#                             '3.0.3239.132 Safari/537.36',
#               'Cookie': 'JSESSIONID=E0C0992130E17FCC974A5E1C760B979C; Hm_lvt_af6f1f256bb28e610b1fc64e6b1a7613=1530165928; Hm_lpvt_af6f1f256bb28e610b1fc64e6b1a7613=1530165982','Origin': 'http://searchweb.miit.gov.cn',
#               'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
#              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#     'Accept': 'application/json, text/javascript, */*; q=0.01', 'Referer': 'http://searchweb.miit.gov.cn/search/search.jsp',
#     'X-Requested-With': 'XMLHttpRequest', 'Connection': 'keep-alive'}
#
#     def __init__(self):
#         db_agent = DatabaseAgent()
#         for page in range(1,146):
#             title = requests.post(
#                 url='http://searchweb.miit.gov.cn/search/search',
#                 headers=self.header,
#                 data='urls=http%3A%2F%2Fwww.miit.gov.cn%2F&sortKey=showTime&sortFlag=-1&fullText=%E5%B7%A5%E4%B8%9A%E4%BA%92%E8%81%94%E7%BD%91&sortType=1&indexDB=css&pageSize=10&pageNow={p}'.format(p=page),
#             )
#             title = json.loads(title.content)
#             for data in title["array"]:
#                 print(data["url"])
#                 url_exits = db_agent.get(
#                     orm_model=Gongxinbu,
#                     filter_kwargs={"url":data["url"]}
#                 )
#                 if url_exits:
#                     print("-----------already exits------------")
#                     continue
#                 self.save_data(data["name"],data["url"])
#
#     def save_data(self,name,url):
#         db_agent = DatabaseAgent()
#         data = requests.get(
#             url=url,
#             headers=self.header,
#         )
#         html = data.content.decode("utf8")
#         data = clear(filter_tags(html))
#         s = IndustrialItem()
#         s["name"] = name
#         s["url"] = url
#         s["data"] = data
#         print(s)
#         try:
#             db_agent.add(
#                 kwargs=dict(s),
#                 orm_model=Gongxinbu
#             )
#             print("-----------add success------------")
#         except:
#             pass
#
#
