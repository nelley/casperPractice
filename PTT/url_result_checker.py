from bson.json_util import dumps
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from mongo_driver import *
import json






logging.basicConfig(level=logging.DEBUG)

# init logger
logger = logging.getLogger('result_checker')
handler = RotatingFileHandler('/home/nelley/casperPractice/PTT/log_PTT_crawler.txt', maxBytes=1024*1024*5, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)



if __name__ == '__main__':
    logger.debug('result checker start')
    param = sys.argv
    category = param[1]
    logger.debug('category:%s' % category)
    try:
        conn = get_db()
        logger.debug('DB connected')
        result = conn.update_Logs.find({'category': category, 'result':{'$exists':True}}, {'result':1, 'lastURL':1}).sort("date",-1).limit(1)
        output = dumps(result)
        logger.debug('output:%s' % output)
        sys.stdout.write(output)
        logger.debug('result checker finished')
    except Exception as e:
        logger.debug('db query error: %s' % e)
        sys.stdout.write('db query error')

