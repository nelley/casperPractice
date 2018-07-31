# -*- coding: utf-8 -*-
import sys
import os
import json
from bson.json_util import dumps
import logging
from logging.handlers import RotatingFileHandler

sys.dont_write_bytecode=True

logging.basicConfig(level=logging.DEBUG)
# init logger
logger = logging.getLogger('mongo_driver')
handler = RotatingFileHandler('/home/nelley/casperPractice/PTT/log_url_updater.txt', maxBytes=1024*1024, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)



Posts_attr=['category', 'url', 'postId', 'ipaddr', 'content', 'post_time', 'modified_time', 'title']

def get_db():
    from pymongo import MongoClient
    client = MongoClient('192.168.8.129:27017')
    db = client.PTT
    db.authenticate("root", "notsniw0405", source="admin")
    return db

def add_post(db, collection):
    db[collection].insert({"category" : "gossip", "text":"test"})
    
def get_post_find_one(db, collection):
    return db[collection].find_one()

def get_post_all(db,collection):
    return db[collection].find()

def remove_documents(db, collection):
    return db[collection].delete_many({})

# args
# arg 1: fetch data from mongodb from URL_list by category
if __name__ == "__main__":
    logger.debug('mongo driver start')
    param = sys.argv
    category = param[1]
    logger.debug('category:%s' % category)

    try:
        db = get_db()
        results = db.URL_list.find({'category':category, 'is_content_updated':False},  {'url':1})
        sys.stdout.write(dumps(results))

        #logger.debug('results:%s' % dumps(results))
        logger.debug('query result count:%s' % results.count())
        #logger.debug('db query finished')
    except Exception as e:
        sys.stdout.write('db query error')
        logger.debug('db query error:%s' % e)

