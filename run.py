'''
TODO
- call issue
'''

from datetime import datetime, timedelta
import json
import os
import subprocess
import time

def crawl_day_page(year=2008, month=1, day=1):
    current_date = datetime(year, month, day)
    delta = timedelta(1)
    while current_date < datetime(2013, 1, 1):
        cd = current_date
        print 'Fetching %d-%02d-%02d'%(cd.year, cd.month, cd.day)
        outfile = 'reuters/%04d%02d%02d.json'%(cd.year, cd.month, cd.day)
        if not os.path.exists(outfile):
            subprocess.call('scrapy crawl RawSpider \
                                -a year=%d -a month=%d -a day=%d \
                                -o %s -t json 2>NULL'%(
                                cd.year, cd.month, cd.day, outfile),
                            shell=True)
        try:
            news = json.load(open(outfile))
            current_date += delta
        except Exception:
            print '- Error!'
            os.remove(outfile)
            time.sleep(10)
if __name__ == '__main__':
    crawl_day_page()

