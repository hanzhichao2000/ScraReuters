ScraReuters
===========

A crawler for Reuters Archives.


Usage
`````

Make sure ``scrapy`` and ``nltk`` are installed.

- Run ``./ScraReuters.py fetch`` to fetch the news. The articles are saved in json in the folder ``reuters`` in the current directory.
- Run ``./ScraReuters.py show`` to get some statistics on the sectors of the fetched news.


During fetching, the output info like ``the law firm of levi & korsinsky , llp announces investigation into possible breaches of fiduciary duty by the board of nyse euronext , inc . in connection with the sale of the company to intercontinentalexchange , inc . ['nyx']`` means that the title is supposed to be related to the stock symbol 'nyx', though it may be inaccurate.

Issues
``````

Due to the update of Reuters website, the identification of stock symbols doesn't work. A simple manual detection is used, which usually makes mistake. The rules are defined in ``ScraReuters/static/company.csv``.
