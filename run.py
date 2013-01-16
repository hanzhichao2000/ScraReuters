'''
TODO
- call issue
'''

import subprocess
from datetime import datetime, timedelta

def crawl_day_page(year=2007, month=1, day=1):
    current_date = datetime(year, month, day)
    delta = timedelta(1)
    while current_date < datetime(2013, 1, 1):
        subprocess.call('scrapy RawCrawler -a year=%d month=%d day=%d \
                            -o reuters%4d%2d%2d.json -t json'%[
                            current_date.year,
                            current_date.month,
                            current_date.day,
                            current_date.year,
                            current_date.month,
                            current_date.day],
                        shell=True)
        break
if __name__ == '__main__':
    crawl_day_page()

