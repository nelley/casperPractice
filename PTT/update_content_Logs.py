# -*- coding: utf-8 -*-
from mongo_driver import *
from datetime import datetime
import sys
import json
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(level=logging.DEBUG)
# init logger
logger = logging.getLogger('update_content_logs')
handler = RotatingFileHandler('/home/nelley/casperPractice/PTT/log_PTT_crawler.txt', maxBytes=1024*1024*5, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)


if __name__ == '__main__':
    #param = sys.argv
    #print sys.stdin.readlines()
    logger.debug('update content logs start')
    data = json.load(sys.stdin)

    conn = get_db()
    conn.update_content_Logs.insert({'log_content':data['log'],
                                    'category':data['category'],
                                    'elapsed_time':data['elapsed_time'],
                                    'date':datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                                    })

