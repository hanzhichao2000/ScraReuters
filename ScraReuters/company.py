import re
from nltk.tokenize import WordPunctTokenizer as WPTker

from ScraReuters import config

class CompanyAlias:
    def __init__(self):
        fr = open('%s/company.csv'%config.ROOT_STATIC)
        self.stocks = {}
        for line in fr.readline().split('\r'):
            line = re.sub('\s+', ' ', line)
            line = line.lower()
            if len(line) == 0:
                continue
            items = line.split(',')
            for i in items:
                if len(i) == 0:
                    items.remove(i)
            symbol = items[0].lower()
            if items[-1] == 'no_short':
                no_short = True
                alias = [i.lower() for i in items[2: -1]]
            else:
                no_short = False
                alias = items[1:]
            self.stocks[symbol] = [no_short, alias]
        fr.close()

company_alias = CompanyAlias()
black_list = ['dow jones', 'FRN Variable Rate Fix']


tker = WPTker()

def get_symbols_in_title(title):
    title = title.lower()
    stocks = []
    for w in black_list:
        if w.lower() in title:
            return []

    for s, v in company_alias.stocks.items():
        tokens = tker.tokenize(title)
        for a in v[1]:
            if s not in stocks:
                if len(a.split(' ')) > 1:
                    if a in title:
                        stocks.append(s)
                else:
                    if a in tokens:
                        stocks.append(s)
        if not v[0]: #not NO_SHORT
            if s in tokens and s not in stocks:
                stocks.append(s)
    return stocks