# -*- coding: utf-8 -*-
from mongo_driver import *
from datetime import datetime
import sys
import json
import logging
from logging.handlers import RotatingFileHandler

# init logger
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('update_Logs')
handler = RotatingFileHandler('/home/nelley/casperPractice/PTT/log_PTT_crawler.txt', maxBytes=1024*1024*5, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)
                                                                                                                             



if __name__ == '__main__':
    #param = sys.argv
    logger.debug('update_Logs start')
    data = json.load(sys.stdin)
    logger.debug('category:%s' % data['category'])
    
    conn = get_db()
    conn.update_Logs.insert({'log_content':data['log'],
                            'category':data['category'],
                            'update_cnt':data['update_cnt'],
                            'insert_cnt':data['insert_cnt'],
                            'elapsed_time':data['elapsed_time'],
                            'lastURL':data['lastURL'],
                            'result':data['result'],
                            'date':datetime.now()
                            })
    logger.debug('update_Logs end')
