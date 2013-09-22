#!/usr/bin/python

from datetime import datetime, timedelta
import json
import os
import sys
import subprocess
import time
from collections import defaultdict

import numpy

def crawl_day_page(year=2012, month=12, day=31):
    '''Fetch the news since the given day

    :type year: int
    :type month: int
    :type day: int
    '''
    current_date = datetime(year, month, day)
    delta = timedelta(1)

    error_dates = []

    counter = 10
    while current_date > datetime(2007, 1, 1):
        cd = current_date
        print 'Fetching %d-%02d-%02d' % (cd.year, cd.month, cd.day)
        outfile = 'reuters/%04d%02d%02d.json' % (cd.year, cd.month, cd.day)
        if not os.path.exists(outfile):
            subprocess.call(
                'scrapy crawl ReutersSpider -a year=%d -a month=%d -a day=%d \
                    -o %s -t json --nolog' % (
                cd.year, cd.month, cd.day, outfile),
                shell=True)
        try:
            json.load(open(outfile))
            current_date -= delta
            print '\t done!'
            counter = 10
        except Exception as e:
            print e
            print '- Error! And there are %d more times!' % counter
            os.remove(outfile)
            time.sleep(5)
            if counter == 0:
                error_dates.append(str(cd))
                current_date -= delta
                continue
            counter -= 1


def show_statistics():
    current_date = datetime(2007, 1, 1)
    delta = timedelta(1)
    
    stats = defaultdict(list)

    sector_set = set()

    while current_date.month <= 7:
        cd = current_date
        day_stats = defaultdict(int)
        articles = json.load(open('reuters/%4d%02d%02d.json' % (cd.year, cd.month, cd.day)))
        for a in articles:
            for s in a['sectors']:
                sector_set.add(s)
        
        current_date += delta
    
    current_date = datetime(2007, 1, 1)
    while current_date.month <= 7:
        cd = current_date
        day_stats = defaultdict(int)
        articles = json.load(open('reuters/%4d%02d%02d.json' % (cd.year, cd.month, cd.day)))
        for a in articles:
            for s in a['sectors']:
                day_stats[s] += 1

        for s in sector_set:
            stats[s].append(day_stats[s])
        
        current_date += delta
    
    print 'Sectors,Mean,Var'
    for s in stats:
        print '%s,%f,%f' % (s, numpy.mean(stats[s]), numpy.var(stats[s]))

def main():
    assert len(sys.argv) >= 2
    cmd = sys.argv[1]
    if cmd == 'fetch':
        crawl_day_page()
    elif cmd == 'show':
        show_statistics()


if __name__ == '__main__':
    try:
        import scrapy
        import nltk
        main()
    except ImportError as e:
        print e
        print 'Please install scrapy and nltk first. Thanks.'
    
    
