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



import urllib
import re
import os
import nltk
import time


import dateutil.parser as du_parser

from comm.CompanyList import *

class MediaType:
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

class Reuters:
    def __init__(self, year, media_filters = [PRN(), BW(), MW(), GNW()]):
        self.year = year
        self.day_links = []
        self.filters = media_filters
        self.nw_stat = {}
        self.stock_stat = {}
    def fetch_day_links(self):
        url = 'http://www.reuters.com/resources/archive/us/%d.html'%self.year
        page = urllib.urlopen(url).read()
        self.day_links = ['http://www.reuters.com'+lnk for lnk in re.findall('<a href="(/resources/archive/us/\d{8}.html)">', page)]

    def check(self, url):
        for f in self.filters:
            if f.check(url):
                return f.name
        return None

    def related_stocks(self, title):
        return which_company_in_title(title)

    def analyze_article_links(self, day_lnk):
        day_tag = day_lnk.split('/')[-1].split('.')[0]
        root = 'resource/reuters2'
        if not os.path.exists('%s/day_tag'%root):
            os.mkdir('%s/day_tag'%root)
        if os.path.exists('%s/day_tag/%s'%(root, day_tag)):
            return
        page = urllib.urlopen(day_lnk).read()
        targets = re.findall('<div class="headlineMed">[\s\S]+?</a>', page)
        articles = {}
        for t in targets:
            if not 'article' in t:
                continue
            match = re.search('<a href=\'(\S+?)\'>([\s\S]+)</a>', t)
            if match == None:
                continue
            [url, title] = [match.group(1), match.group(2)]
            name = self.check(url)
            if not name == None:
                if 'C O R R E C T I O N' in title:
                    continue
                stocks = self.related_stocks(title)
                if len(stocks) > 0:
                    self.stock_stat_do(stocks)
                    self.nw_stat_do(name)
                    for s in stocks:
                        if not articles.has_key(s):
                            articles[s] = []
                        articles[s].append([title, url])
        self.save_articles(articles, day_tag)

        for s in articles.keys():
            for item in articles[s]:
                title = item[0]
                url = item[1]
                try:
                    [raw_date, text] = self.get_article_from_url(url)
                except:
                    continue
                self.save_article(s, raw_date, title, text)

    def save_articles(self, articles, day_tag):
        root = 'resource/reuters2'
        if os.path.exists('%s/day_tag/%s'%(root, day_tag)):
            return


        for s, v in articles.items():
            if not os.path.exists('%s/%s'%(root, s)):
                os.mkdir('%s/%s'%(root, s))

            fw = open('%s/%s/%s'%(root, s, day_tag), 'w+')
            for i in v:
                fw.write('%s/!/!/!/%s\n'%(i[0], i[1]))
            fw.close()

        open('%s/day_tag/%s'%(root, day_tag), 'w+').close()

    def save_article(self, stock, raw_date, title, text):
        root = 'resource/raw_data/raw_reuters'
        title = re.sub('\W+', ' ', title)
        title = re.sub('\s+', ' ', title)
        output_file = '%s/%s__%s__%s'%(root, stock, raw_date, title[:10])
        if os.path.exists(output_file):
            return

        open(output_file, 'w+').write(title+'\n'+text)


    def stock_stat_do(self, stocks):
        for s in stocks:
            if not self.stock_stat.has_key(s):
                self.stock_stat[s] = 1
            else:
                self.stock_stat[s] += 1

    def nw_stat_do(self, name):
        '''news wire statistics'''
        if self.nw_stat.has_key(name):
            self.nw_stat[name] += 1
        else:
            self.nw_stat[name] = 1

    def get_article_from_url(self, url):
        content = urllib.urlopen(url).read()
        match = re.search('<span class="focusParagraph">([\s\S]+?)<div id="relatedStocks2">', content)
        text = nltk.clean_html(match.group(0))

        match = re.search(r'<div id="articleInfo">\s*<p>\s*<span class="timestamp">([\s\S]+?)</span>', content)
        raw_date = match.group(1)
        ts_date = time.mktime(du_parser.parse(raw_date).timetuple())
        hr = 60*60
        if raw_date.upper().endswith('EDT'):
            ts_date += 4*hr
        elif raw_date.upper().endswith('EST'):
            ts_date += 5*hr
        else:
            return None
        return [ts_date, text]
