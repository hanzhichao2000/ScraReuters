'''
TODO
- call issue
'''

import subprocess
from datetime import datetime, timedelta

def crawl_day_page(year=2008, month=1, day=1):
    current_date = datetime(year, month, day)
    delta = timedelta(1)
    while current_date < datetime(2013, 12, 1):
        cd = current_date
        print 'Fetching %d-%02d-%02d'%(cd.year, cd.month, cd.day)
        subprocess.call('scrapy crawl RawSpider \
                            -a year=%d -a month=%d -a day=%d \
                            -o news/reuters%d%02d%02d.json -t json 2> log'%(
                            cd.year, cd.month, cd.day,
                            cd.year, cd.month, cd.day),
                         shell=True)
        current_date += delta
if __name__ == '__main__':
    crawl_day_page()

