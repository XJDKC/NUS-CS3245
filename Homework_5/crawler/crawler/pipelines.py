# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
from collections import OrderedDict
from scrapy.exceptions import DropItem

class CrawlerPipeline:

    def open_spider(self, spider):
        self.dataset = OrderedDict()
        self.fields = ['docid','url','title', 'date', 'authors', 'content', 'outlinks']

    def process_item(self, item, spider):
        if item['url'] in self.dataset:
            raise DropItem("Duplicate book found:%s" % item)

        item['docid'] = len(self.dataset)
        self.dataset[item['url']] = item

        return item

    def close_spider(self, spider):
        with open('data.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            for url in self.dataset:
                item = self.dataset[url]

                ids = []
                for outlink in item['outlinks']:
                    ids.append(str(self.dataset[outlink]['docid']))
                item['outlinks'] = ' '.join(ids)

                values = [item[field] for field in self.fields]
                csvwriter.writerow(values)
