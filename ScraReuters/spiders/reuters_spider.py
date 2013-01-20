'''
The spider for reuters.

TODO:
- Parse raw date.

'''

from datetime import datetime
import re

from dateutil.parser import parse

import nltk
from nltk.tokenize import WordPunctTokenizer as WPTker

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

from ScraReuters.items import NewsItem
from ScraReuters.company import get_symbols_in_title

class MediaType:
    '''The base type of wire media'''
    def __init__(self, name, re):
        self.name = name
        self.re = re
    def check(self, url):
        return self.re.search(url) != None

PRN_REG = re.compile('\+PRN\d{8}')
BW_REG = re.compile('\+BW\d{8}')
MW_REG = re.compile('\+MW\d{8}')
GNW_REG = re.compile('\+GNW\d{8}')

class PRN(MediaType):
    def __init__(self):
        MediaType.__init__(self, 'PRN', PRN_REG)

class BW(MediaType):
    def __init__(self):
        MediaType.__init__(self, 'BW', BW_REG)

class MW(MediaType):
    def __init__(self):
        MediaType.__init__(self, 'MW', MW_REG)

class GNW(MediaType):
    def __init__(self):
        MediaType.__init__(self, 'GNW', GNW_REG)

MEDIA_FILTERS = [PRN(), BW(), MW(), GNW()]

def is_wire(url):
    '''Checks if a URL is a type of wire media'''
    for filter in MEDIA_FILTERS:
        if filter.check(url):
            print url
            return True
    return False

tker = WPTker()

def normalize_title(title):
    title = re.sub('Reuters', '', title)
    title = re.sub('\|', '', title)
    tokens = [e.lower() for e in tker.tokenize(title)]
    return ' '.join(tokens)
    

class ReutersSpider(BaseSpider):
    name = 'ReutersSpider'
    allowed_domains = ['reuters.com']

    def __init__(self, year, month, day):
        year, month, day = [int(e) for e in [year, month, day]]
        self.date = datetime(year, month, day)
        self.start_urls = ['http://www.reuters.com/resources/archive/us/%4d%02d%02d.html'%(year, month, day)]
        self.is_index = True

    def parse(self, response):
        if self.is_index:
            return self.parse_index(response)
        else:
            return self.parse_news(response)

    def parse_index(self, response):
        '''Parses the index page'''
        self.is_index = False
        hxs = HtmlXPathSelector(response)
        
        self.titles = {}
        for target in hxs.select('//div[@class="headlineMed"]'):
            title = normalize_title(target.select('a/text()').extract()[0])
            link = target.select('a/@href').extract()[0]
            #str_time = item.select('text()').extract()[0][1:]
            #time = parse(str_time)
            if 'C O R R E C T I O N' in title or title in self.titles:
                continue
            
            if link.startswith('http://www.reuters.com/news/video/'):
                continue
            
            self.titles[title] = link
            yield Request(link, callback=self.parse_news)
    
    @staticmethod
    def find_symbols(body):
        '''
        e.g. The script in the html is like
        <script type="text/javascript">
                Reuters.info.sRelatedStocks = 'VOD.L,LAND.L,RBS.L,LSE.L,NDAQ.O';
        </script>
        '''
        raw_symbols = re.findall('Reuters.info.sRelatedStocks = \'([\w\.\,\d]+)\';', body)
        if len(raw_symbols) > 0:
            return raw_symbols[0].split(',')
        else:
            return []
    
    def parse_news(self, response):
        '''Parses news pages'''
        hxs = HtmlXPathSelector(response)
        item = NewsItem()
        raw_title = hxs.select('//title/text()').extract()[0]
        item['title'] = normalize_title(raw_title)
        item['link'] = response.url
        
        # Gets symbols from the page
        item['symbols'] = ReutersSpider.find_symbols(response.body)
        
        # Return None if no symbol is found
        if not len(item['symbols'])>0:
            return
        
        # Gets text from the page
        item['text'] = ''
        for target in hxs.select('//div[@id="articleContent"]/div[@class="sectionContent"]'):
            for p in target.select('//p'):
                raw_text = p.extract()
                item['text'] += nltk.clean_html(raw_text)
        
        raw_date = hxs.select('//div[@id="articleInfo"]/p/span[@class="timestamp"]/text()').extract()
        item['date'] = raw_date
        
        return item