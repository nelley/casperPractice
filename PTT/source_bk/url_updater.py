# -*- coding: utf-8 -*-

# url_updater.py
# update url list in database

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
from collections import Counter


reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig(level=logging.DEBUG)

# init logger
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('log_url_updater.txt', maxBytes=1024*1024, backupCount=2)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)

ent_object = []
UPDATE_INTERVAL = 2

class ent(object):
    def __init__(self, url, comment_cnt, date, mark):
        self.url = url
        self.comment_cnt = comment_cnt
        self.date = date
        self.mark = mark

    def print_all(self):
        logger.debug('url=%s comment_cnt=%s date=%s mark=%s' % (self.url, self.comment_cnt, self.date, self.mark))





'''get most frequent date in the array'''
def date_process():
    logger.debug('date process start')
    tmp_dates = []
    for obj in ent_object:
        tmp_dates.append(obj.date)
    
    f_date = Counter(tmp_dates)
    
    logger.debug('date process finished')

    return datetime.strptime(f_date.most_common(1)[0][0], '%m/%d')    


def db_connect():
    try:
        conn=psycopg2.connect("dbname='ptt' user='postgres' host='192.168.8.129' password='notsniw0405'")
        conn.autocommit = True
    except Exception as e:
        logger.debug('db_connect error= %s' % e)
        sys.stdout.write('db connection error') 
        sys.exit() 
    return conn

'''for query: By same url'''
def db_query(conn, obj):
    logger.debug('db query start')
    cur = conn.cursor()
    rows = []
    try:
        cur.execute("SELECT comment FROM url_list_techjob WHERE url=%s", (obj.url,))
        rows = cur.fetchall()
    except Exception as e:
        logger.debug('db_query error= %s' % e)
        sys.stdout.write('db query error')
        sys.exit() 

    cur.close()
    return rows

'''for insert'''
def db_insert(conn, obj):
    logger.debug('db insert start')
    cur = conn.cursor() 
    now_t = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    try:
        cur.execute('INSERT INTO url_list_techjob (url, comment, created_date, modified_date, mark, is_content_updated) VALUES (%s, %s, %s, %s, %s, False)', 
                    (obj.url, obj.comment_cnt, now_t, now_t, obj.mark))
    except Exception as e:
        logger.debug('db_insert error= %s' % e)
        sys.stdout.write('db insert error')
        sys.exit() 

    cur.close()


''' db update '''
def db_update(conn, obj):
    logger.debug('db update start')
    cur = conn.cursor()
    now_t = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    try:
        cur.execute('UPDATE url_list_techjob SET comment=%s, modified_date=%s, is_content_updated=False WHERE url=%s;', (obj.comment_cnt, now_t, obj.url))
    except Exception as e:
        logger.debug('db_update error=%s' % e)
        sys.stdout.write('db update error')
        sys.exit() 

    cur.close()


'''decide update range by date'''
def techjob_updater():
    logger.debug('techjob_updater start')

    db_conn = db_connect()
    
    for obj in ent_object:
        if obj.url:     #if article is deleted by board admin, it will never got updated
            today_date =  datetime.strptime(datetime.now().strftime("%m/%d"), '%m/%d')
            std = today_date - most_frequent_day
            
            #first check update range
            if std.days < UPDATE_INTERVAL:
                # check already exist or not
                result_comment = db_query(db_conn, obj)
                logger.debug('url=%s today_date=%s most_frequent_day=%s std.days=%s result_comment=%s' % (obj.url, today_date, most_frequent_day, std.days, result_comment)) 
                if not result_comment:
                    # if no data in db, insert it
                    result = db_insert(db_conn, obj)

                elif( "".join([x[0] for x in result_comment]) == obj.comment_cnt):
                    # if no change
                    logger.debug("comment count is the same!")

                else:
                    # if comment cnt changed, update the row
                    logger.debug("Before:%s, After:%s" % (result_comment[0], obj.comment_cnt))
                    result = db_update(db_conn, obj)

            else:   # end whole update process
                logger.debug('out of the update range url=%s' % obj.url)
                sys.stdout.write('encountered over-ranged article')
                sys.exit()
        else:
            logger.debug('no url: date=%s, comment=%s' % (obj.date, obj.comment_cnt))
        
        logger.debug('one of the obj in ent_object processed')

    logger.debug('techjob_updater finished')                    

'''parse html into ent_object array'''
def html_parser(urls):
    logger.debug('html_parser start')

    soup = BeautifulSoup(urls, "html.parser")
    for obj in soup.findAll('div', {"class","r-ent"}):
        # get comment_cnt
        comment_cnt = obj.find('span')
        if comment_cnt is None:
            comment_cnt = '0'
        else:
            comment_cnt = comment_cnt.text.strip().encode('utf-8')

        # get date
        date = obj.find('div', {"class","date"})
        if date is None:
            date = 'None'
        else:
            date = date.text.strip().encode('utf-8')
       
        # get url
        tmp_url = obj.a
        if tmp_url is not None:
            url = tmp_url['href']
        else:
            url = ''
        
        # get mark 
        mark = obj.find('div', {"class","mark"})
        if len(mark.text) == 0:
            mark = ''
        else:
            mark = mark.text.strip().encode('utf-8')

        ent_object.append(ent(url, comment_cnt, date, mark))
 
    logger.debug('html_parser finished')

if __name__ == "__main__":
    logger.debug('main start')
    param = sys.argv

    #process url list
    html_parser(param[1])
    
    # get most frequent date
    most_frequent_day = date_process()

    techjob_updater()
    
    #countinue the update process to next url 
    sys.stdout.write('done')


