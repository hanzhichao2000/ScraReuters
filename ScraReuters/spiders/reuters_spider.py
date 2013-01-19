'''
TODO
- Details of the page
'''

from datetime import datetime
from dateutil.parser import *

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

from ScraReuters.items import NewsItem
from ScraReuters.company import get_symbols_in_title

class ReutersSpider(BaseSpider):
    name = 'ReutersSpider'
    allowed_domains = ['reuters.com']


    def __init__(self, year, month, day):
        year, month, day = [int(e) for e in [year, month, day]]
        self.date = datetime(year, month, day)
        self.start_urls = ['http://www.reuters.com/resources/archive/us/%4d%02d%02d.html'%(year, month, day)]
        self.is_index = True

    def parse(self, response):
        print self.start_urls
        if self.is_index:
            return self.parse_index(response)
        else:
            return self.parse_news(response)

    def parse_index(self, response):
        self.is_index = False
        hxs = HtmlXPathSelector(response)
        for target in hxs.select('//div[@class="headlineMed"]'):
            title = target.select('a/text()').extract()[0]
            link = target.select('a/@href').extract()[0]
            #str_time = item.select('text()').extract()[0][1:]
            #time = parse(str_time)
            if link.startswith('http://www.reuters.com/news/video/'):
                continue
            symbols = get_symbols_in_title(title)
            if len(symbols)>0:
                print symbols
                yield Request(link, callback=self.parse_news)
        yield None


    def parse_news(self, response):
        return None
