# __coding:utf-8__
'''
@Author  : 朱晓扬
@Time    :  下午8:52
@Software: PyCharm
@File    : job_run.py
'''

import os
import sys
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(['scrapy', 'crawl', 'zhilian_python', '-o', './export/items.json'])
# execute(['scrapy', 'crawl', 'shanghai'])
execute(['scrapy', 'crawl', 'anhui'])
