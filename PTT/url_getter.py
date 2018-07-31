# -*- coding: utf-8 -*-
import sys
import os
import json
from bson.json_util import dumps
import logging
from logging.handlers import RotatingFileHandler
from mongo_driver import *
from random import shuffle

logging.basicConfig(level=logging.DEBUG)
# init logger
logger = logging.getLogger('url_getter')
handler = RotatingFileHandler('/home/nelley/casperPractice/PTT/log_PTT_crawler.txt', maxBytes=1024*1024*5, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)


# args
# arg 1: fetch data from mongodb from URL_list by category
if __name__ == "__main__":
    logger.debug('url getter start')
    param = sys.argv
    category = param[1]
    logger.debug('category:%s' % category)

    try:
        logger.debug('db query start')
        db = get_db()
        logger.debug('db connected:%s' % db)
        
        results = db.URL_list.find({'category':category, 'is_content_updated':False, 'is_deleted':False},  {'url':1}).limit(50000)

        results = list(results)
        shuffle(results)

        #logger.debug('query result count:%s' % results.count())
        logger.debug('query result count:%s' % len(results))
        output = dumps(results)
        #for item in results: 
        logger.debug('results:%s' % output)
        sys.stdout.write(output)

        #logger.debug('db query finished')
    except Exception as e:
        logger.debug('db query error:%s' % e)
        sys.stdout.write('db query error')

