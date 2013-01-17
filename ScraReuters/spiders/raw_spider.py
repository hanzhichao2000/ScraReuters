'''
TODO
- Fix time zone conversion
'''

from datetime import datetime
from dateutil.parser import *

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from ScraReuters.items import RawItem

class RawSpider(BaseSpider):
    name = 'RawSpider'
    allowed_domains = ['reuters.com']

    def __init__(self, year, month, day):
        year, month, day = [int(e) for e in [year, month, day]]
        self.date = datetime(year, month, day)
        self.start_urls = ['http://www.reuters.com/resources/archive/us/%4d%02d%02d.html'%(year, month, day)]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        items = []
        for target in hxs.select('//div[@class="headlineMed"]'):
            item = RawItem()
            item['title'] = target.select('a/text()').extract()[0]
            item['link'] = target.select('a/@href').extract()[0]
            #str_time = item.select('text()').extract()[0][1:]
            #time = parse(str_time)
            if not item['link'].startswith('http://www.reuters.com/news/video/'):
                items.append(item)
        return items
