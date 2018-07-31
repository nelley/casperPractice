# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import bs4
import urllib2
import sys
import os
import csv
import re
import psycopg2
import logging
from logging.handlers import RotatingFileHandler
from shutil import copyfile
from datetime import datetime



reload(sys)
sys.setdefaultencoding('utf-8')
# init logger
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('postgresDB connector')
handler = RotatingFileHandler('log_url_updater.txt', maxBytes=1024*1024, backupCount=2)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)


def db_connect():
    try:
        conn=psycopg2.connect("dbname='ptt' user='postgres' host='192.168.8.129' password='notsniw0405'")
        conn.autocommit = True
    except Exception as e:
        logger.debug('db_connect error= %s' % e)
        sys.stdout.write('db connection error')
        sys.exit()
    return conn


'''for query: get url by '''
def db_query(conn):
    logger.debug('db query start')
    cur = conn.cursor()
    rows = []
    try:
        cur.execute("SELECT url FROM url_list_techjob WHERE is_content_updated = 'false'")
        rows = cur.fetchall()
    except Exception as e:
        logger.debug('db_query error= %s' % e)
        sys.stdout.write('db query error')
        sys.exit()

    cur.close()
    
    rows.insert(0, 'done')

    return json.dumps(rows)




if __name__ == "__main__":
    logger.debug('main start')
    param = sys.argv

    conn = db_connect()

    sys.stdout.write(db_query(conn))

    
