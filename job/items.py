
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    jobname = scrapy.Field()
    url = scrapy.Field()
    origin = scrapy.Field()
    money = scrapy.Field()
    natural = scrapy.Field()
    exp = scrapy.Field()
    education = scrapy.Field()
    time = scrapy.Field()
    com_id = scrapy.Field()
    city = scrapy.Field()
    description = scrapy.Field()

class IndustrialItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    # data = scrapy.Field()
    area = scrapy.Field()
    origin = scrapy.Field()
    nature = scrapy.Field()
    time = scrapy.Field()
