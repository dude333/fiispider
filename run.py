#!/usr/local/bin/python3

from scrapy.crawler import CrawlerProcess
from fiispider import FIISpider
import logging
import sys
import re

if len(sys.argv) < 2:
    print("Entre com o CNPJ do FII")
    quit()

cnpj_arg = re.sub("[^0-9]", "", sys.argv[1])
n_arg = sys.argv[2] if len(sys.argv) > 2 else 3

logging.disable(logging.WARNING)

process = CrawlerProcess(
    {"USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"}
)

process.crawl(FIISpider, cnpj=cnpj_arg, n=n_arg)
process.start()  # the script will block here until the crawling is finished
