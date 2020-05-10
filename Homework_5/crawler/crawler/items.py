# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    docid = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    authors = scrapy.Field()
    content = scrapy.Field()
    urls = scrapy.Field()

    pass
