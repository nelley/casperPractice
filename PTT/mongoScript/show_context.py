from bson.json_util import dumps
import time
import os
import sys
# add the directory that python will search for
sys.path.insert(0, '/home/nelley/casperPractice/PTT')
from mongo_driver import *

def url_grabber_checker(category):
    start_time = time.time()
    #check URL_GRABBER is done or not
    result = conn.update_Logs.find({'category': category, 'result':{'$exists':True}}, {'result':1, 'lastURL':1}).sort("date",-1).limit(1)
    print '%s, %0.2f seconds' % (dumps(result), time.time()-start_time)
    
def wait_crawl_post_count(category):
    start_time = time.time()
    result = conn.URL_list.find({'category':category, 'is_content_updated':False, 'is_deleted':False}).count()
    print 'Number of uncollected Posts:%s, %0.2f seconds' % (result, time.time()-start_time)

def latest_content_checker(category):
    start_time = time.time()
    result = conn.Posts.find({'category':category}).sort("post_time",-1).limit(5)
    for doc in result:
        print '%s, "%s"' % (doc['title'], doc['post_time'])
    print '%0.2f seconds' % (time.time()-start_time)

def collected_post_count(category):
    start_time = time.time()
    result = conn.Posts.find({'category':category}).count()
    print 'Number of collected Posts:%s, %0.2f seconds' % (result, time.time()-start_time)

def content_updated_count(category):
    start_time = time.time()
    result = conn.URL_list.find({'category':category, 'is_content_updated':True}).count()
    print '# of updated contents:%s, %0.2f seconds' % (result, time.time()-start_time)

if __name__ == '__main__':
    param = sys.argv
    category = param[1]
    print 'category:%s' % category
    try:
        conn = get_db()
        print 'DB connected'
        wait_crawl_post_count(category)
        url_grabber_checker(category)
        latest_content_checker(category)
        print '-------------------------------------'
        collected_post_count(category)
        content_updated_count(category)
        print 'finished'
    except Exception as e:
        print 'Exception:%s' % e
