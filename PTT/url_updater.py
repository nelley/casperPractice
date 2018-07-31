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
from mongo_driver import *
import json
import time


reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig(level=logging.DEBUG)

# init logger
logger = logging.getLogger('url_updater')
handler = RotatingFileHandler('/home/nelley/casperPractice/PTT/log_PTT_crawler.txt', maxBytes=1024*1024*5, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)

ent_object = []
stdout_json = {}
UPDATE_INTERVAL =5 
# list for append urls
wait_insert_url=[]
wait_update_url=[]

'''
storing object from the url_grabber.js
'''
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


'''for query: By same url'''
def db_query(conn, obj):
    logger.debug('db query start')
    try:
        # SELECT comment from URL_list WHERE url=obj.url
        result = conn.URL_list.find_one({"url":obj.url}, {'comment':1})
    except Exception as e:
        logger.debug('db_query error= %s' % e)
        stdout_json['result'] = 'db query error'
        sys.stdout.write(json.dumps(stdout_json))
        sys.stdout.flush()
        sys.exit() 

    return result

'''decide update range by date'''
def url_updater(conn, category):
    logger.debug('url_updater start')
    
    '''
    check all URL_list in db from yesterday(UPDATE_INTERVAL) to now.
    if does not exist: insert
    if existed & comment count is the same: skip
    if existed & comment count is changed: update
    ''' 
    for obj in ent_object:
        if obj.url:     #if article is deleted by board admin, it will never got updated
            today_date =  datetime.strptime(datetime.now().strftime("%m/%d"), '%m/%d')
            std = today_date - most_frequent_day
            
            #first check update range
            if std.days < UPDATE_INTERVAL:
                # check already exist or not
                result = db_query(conn, obj)
                logger.debug('url=%s today_date=%s most_frequent_day=%s std.days=%s' % (obj.url, today_date, most_frequent_day, std.days))
                if result is None:
                    # if no data in db, append it for bulk insert
                    wait_insert_url.append({'url':obj.url,
                                    'category':category, 
                                    'comment':obj.comment_cnt, 
                                    'created_date':obj.date,    #creation date of the post 
                                    'modified_date':datetime.now(),   #change whenever updated
                                    'mark':obj.mark,
                                    'is_content_updated': False,
                                    'is_deleted':False})
                    logger.debug("insert data appended!")

                elif result['comment'] == obj.comment_cnt:
                    # if no change
                    logger.debug("comment count is the same:%s" % result['comment'])

                else:
                    # if comment cnt changed, update the row
                    logger.debug("Before:%s, After:%s" % (result['comment'], obj.comment_cnt))
                    wait_update_url.append({'url': obj.url,
                                        'comment':obj.comment_cnt,
                                        'modified_date':datetime.now(),
                                        'is_content_updated':False})

            else:   # end whole update process
                logger.debug('out of the update range url=%s' % obj.url)
                stdout_json['result'] = 'encountered over-ranged article'
                sys.stdout.write(json.dumps(stdout_json))
                sys.stdout.flush()
                sys.exit()
        else:
            logger.debug('no url: date=%s, comment=%s' % (obj.date, obj.comment_cnt))
        
        logger.debug('one of the obj in ent_object processed')
    
    # insert appended data
    if len(wait_insert_url) > 0:
        try:
            conn.URL_list.insert_many(wait_insert_url)
            logger.debug('bulk insert completed, inserted num:%s' % len(wait_insert_url))
        except Exception as e:
            logger.debug(e)
            stdout_json['result'] = 'db bulk insert error'
            sys.stdout.write(json.dumps(stdout_json))
            sys.stdout.flush()
            sys.exit() 

    # update appended data
    if len(wait_update_url) > 0:
        logger.debug('bulk update start')
        try:
            bulk = conn.URL_list.initialize_unordered_bulk_op()
            for url in wait_update_url:
                bulk.find({"url":obj.url}).update({"$set":{
                                                    "comment":url['comment'],
                                                    "modified_date":url['modified_date'],
                                                    "is_content_updated":url['is_content_updated']}})
            bulk.execute()
            logger.debug('bulk update completed, updated num:%s' % len(wait_update_url))
        except Exception as e:
            logger.debug(e)
            stdout_json['result'] = 'db bulk update error'
            sys.stdout.write(json.dumps(stdout_json))
            sys.stdout.flush()
            sys.exit() 

    # collect data for insert to update_Logs collection
    stdout_json['total_insert'] = len(wait_insert_url)
    stdout_json['total_update'] = len(wait_update_url)
    
    logger.debug('url_updater finished')                    

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
    
    # get mongodb connection
    db_conn = get_db()

    # param[2] is category passed from url_grabber.js
    url_updater(db_conn,param[2])
    
    # retrive html of each url
 
    #countinue the update process to next url
    stdout_json['result'] = 'done' 
    logger.debug('std_json:%s' % json.dumps(stdout_json))
    sys.stdout.write(json.dumps(stdout_json))
    sys.stdout.flush()

    
