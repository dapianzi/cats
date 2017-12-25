# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Imgs(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    img_hash    = scrapy.Field()
    img_src     = scrapy.Field()
    img_desc    = scrapy.Field()
    img_from    = scrapy.Field()
    img_spider  = scrapy.Field()
