#-*- coding=utf-8 -*-
from bson.json_util import dumps
import time
import os
import sys
# add the directory that python will search for
sys.path.insert(0, '/home/nelley/casperPractice/PTT')
from mongo_driver import *
from time import sleep
import re

#####################################
#group2 = dict({"$group":{"_id":{"cate":"$category","author":"$author"}, "details":{"$push":{"agree_cnt":"$agree_cnt","disagree_cnt":"$disagree_cnt"}}}})
#####################################
def clean_by_regex(tmp_s):
     # del url    
     tmp_s = re.sub('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+.*', '', tmp_s)
     # del IP
     tmp_s = re.sub('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '', tmp_s)
     # del comment meta
     tmp_s = re.sub(re.compile(u'^[噓|推|→]\s.*:\s',re.MULTILINE), '', tmp_s)
     tmp_s = re.sub('(\d+/\d+)\s(\d+:\d+)', '', tmp_s)
     # del footer
     tmp_s = re.sub(re.compile(u'^※\s發信站:.*',re.MULTILINE), '', tmp_s)
     tmp_s = re.sub(re.compile(u'^※\s編輯:.*',re.MULTILINE), '', tmp_s)
     tmp_s = re.sub(re.compile(u'^※\s文章網址:.*',re.MULTILINE), '', tmp_s)
     tmp_s = re.sub(u'推文自動更新已關閉', '', tmp_s)
     tmp_s = re.sub(u'批踢踢實業坊', '', tmp_s)
 
     return tmp_s


def get_all_author_post_number():
    start_time = time.time()
    #result = conn.URL_list.find({'category':category, 'is_content_updated':False, 'is_deleted':False}).count()
    #result = conn.Posts.find({'author':'HarryHTC '}).count()

    result = list(conn.Posts.aggregate([{"$group":{"_id":"$author", "post_count":{"$sum":1}}}]))
    sorted_result = sorted(result, key = lambda k:k['post_count'], reverse=True)
    return sorted_result[:10]



    #print 'total author=%s' % len(sorted_result)
    #for post in sorted_result[:10]:
    #    print 'author=%s, count=%s' % (post['_id'],post['post_count'])

def show_post_number_by_category(list_obj):
    for post in list_obj:
        result = conn.Posts.find({'author':post['_id']})
        for item in result:
            if item['author'] == 'yoyodiy ':
                print 'Category=%s, Author=%s' % (item['category'],item['author'])
                print '======================='
                print clean_by_regex(item['content'])
                print '======================='
                sleep(5)


def create_tmp_collection_by_criteria(agree_cnt=0, disagree_cnt=0, fence_cnt=0):
    start_time = time.time()
    #project a new field agree_gteN, disagree_gteN, fence_gteN
    project = dict({"$project":{"author":1, "category":1, "title":1,"post_time":1, "url":1,"content":1,\
                                "agree_cnt":1,"disagree_cnt":1, "fence_cnt":1,\
                                "agree_gteN":{"$gte":["$agree_cnt",agree_cnt]},\
                                "disagree_gteN":{"$gte":["$disagree_cnt",disagree_cnt]},\
                                "fence_gteN":{"$gte":["$fence_cnt",fence_cnt]},\
                                }})
    #only show the matched one(agree_gteN)
    match = dict({"$match":{"agree_gteN":True,"disagree_gteN":True,"fence_gteN":True}})
    #out to the specific collection
    out = dict({"$out":"temp"})
    result = conn.Posts.aggregate([project,match,out])
    print 'out create time=%s' % (time.time() - start_time)



def show_posts_by_author(author_list):
    print '======================================================'
    start_time = time.time()
    for item in author_list:
        result = list(conn.temp.find({'author':item['_id']['author'], 'category':item['_id']['category']}))
        for post in result:
            print '%s,\t%s,\t%s,\n%s' % (post['author'], post['title'], post['post_time'], post['content'])

"""
group by author and get top N posts from specific category
"""
def group_by_author(topN, category):
    print '======================================================'

    match = dict({"$match":{"category":category}})
    group = dict({"$group":{"_id":{"author":"$author", "category":"$category"}, "cnt_by_author":{"$sum":1}}})

    result = list(conn.temp.aggregate([match,group]))
    sorted_result = sorted(result, key = lambda k:k['cnt_by_author'], reverse=True)
    #for item in sorted_result[:topN]:
    #    print '%s, %s, %s' % (item['_id']['author'], item['_id']['category'], item['cnt_by_author'])

    return sorted_result[:topN]


def aggregate_posts_by_author(topN):
    print '======================================================'
    start_time = time.time()

    #grouping and count the number of the posts which agree_cnt gte 99
    group = dict({"$group":{"_id":{"author":"$author"}, "cnt_author":{"$sum":1}}})
    result = list(conn.temp.aggregate([group]))
    sorted_result = sorted(result, key = lambda k:k['cnt_author'], reverse=True)
    print 'out create time=%s' % (time.time() - start_time)
    for item in sorted_result[:10]:
        print item
    print 'hit number=%s' % len(result)
    print 'query time=%s' % (time.time() - start_time)

    print '===============END===================================='

if __name__ == '__main__':
    try:
        conn = get_db()
        print 'DB connected'
        #author_post_count_list = get_all_author_post_number()
        #show_post_number_by_category(author_post_count_list)

        #create_tmp_collection_by_criteria(99,99,99)
        #aggregate_posts_by_author(10)
        show_posts_by_author(group_by_author(10, "gossip"))
        print 'finished'
    except Exception as e:
        print 'Exception:%s' % e




