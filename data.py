# __coding:utf-8__
'''
@Author  : 朱晓扬
@Time    :  下午8:52
@Software: PyCharm
@File    : job_run.py
'''

import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

KEY = os.getenv("KEY", None)

process = CrawlerProcess(get_project_settings())
# process.crawl('shanghai')
# process.crawl('anhui')
# process.crawl('jiangsu')
# process.crawl('chanyelianmeng')
# process.crawl('zhejiang')
# process.crawl('gongxinbu')
# process.crawl('souhu')
# process.crawl('shandong')
process.crawl('zaoqizhineng')



process.start()
