############################################################################
#>python export_CSV_from_mongo.py category start_date end_date
#>python export_CSV_from_mongo.py gossip 2018-1-1 2018-1-31
############################################################################
import io
import json
import traceback
from bson.json_util import dumps
#import datetime
import time
from datetime import datetime
import os
import sys
import csv
import pdb
# add the directory that python will search for
sys.path.insert(0, '/home/nelley/casperPractice/PTT')
from mongo_driver import *

#pdb.set_trace()

#ABS_PATH = '/home/nelley/casperPractice/PTT/mongoScript/export_with_loadfile_gossip/'
#ABS_PATH = '/home/nelley/casperPractice/PTT/mongoScript/export_techjob/'
ABS_PATH = '/home/nelley/casperPractice/PTT/mongoScript/export_texts/'


try:
    to_unicode = unicode
except:
    to_unicode = str

def result_export(category, start, end):
    
    start = datetime(int(start.split('-')[0]),int(start.split('-')[1]),int(start.split('-')[2]),0,0,0)
    end = datetime(int(end.split('-')[0]),int(end.split('-')[1]),int(end.split('-')[2]),23,59,59)
    #result = conn.Posts.find({'category':category}, {'content':1}).sort('post_time',-1).limit(5)
    #result = conn.Posts.find({'category':category}, {'content':1}).sort('post_time',-1)
    #result = conn.Posts.find({'category':category})
    result = conn.Posts.find({'category':category,'post_time':{'$gte':start,'$lt':end}})
    return result

def attr_writer(item):
    
    #ATTR_LIST = ['author', 'category', 'agree_cnt', 'disagree_cnt', 'fence_cnt', 'post_time', 'modified_date', 'title']
    ATTR_LIST_KP = ['author', 'category', 'agree_cnt', 'disagree_cnt', 'fence_cnt', 'post_time', 'modified_date', 'title', 'content']
    result = []

    for a in ATTR_LIST_KP:
        if item[a]:
            #if isinstance(item[a], type(datetime.datetime.now())):
            if isinstance(item[a], type(datetime.now())):
                result.append(item[a].strftime('%Y/%m/%d %H:%M:%S'))
            else:
                tmp = json.dumps(item[a], ensure_ascii=False)
                result.append(tmp.encode('utf-8'))
        else:
            if a == 'post_time':
                result.append(str_post_time)
            elif a == 'modified_date':
                result.append(str_mod_time)
            else:
                result.append('"None"')

    return result

def initialize_loadfile():
    LIV_LIST = ['"APP.author"','"APP.category"','"APP.Comments"','"APP.template"','"APP.Manager"','"APP.Created"','"FS.Last Modified Date"','"APP.Title"','"DOCLINK"', '"TEXTLINK"', '"LIV.Doc ID"']
    with open(ABS_PATH + 'loadfile.txt','a') as tmp_file:
        tmp_file.write(','.join(str(x) for x in LIV_LIST) + '\r\n')
       
def initialize_loadfile_KP():
    LIV_LIST = ['"author"','"category"','"agree"','"disagree"','"fence"','"Created Date"','"Last Modified Date"','"Title"','"Content"']
    with open(ABS_PATH + 'loadfile.txt','a') as tmp_file:
        tmp_file.write(','.join(str(x) for x in LIV_LIST) + '\r\n')
       
def create_text(item, file_name):
    with io.open(ABS_PATH + 'text/'+ file_name +'.txt','w', encoding='utf8') as tmpfile:
        str_ = json.dumps(item['content'], ensure_ascii=False)
        str_ = str_.replace('\\n', '\n')
        tmpfile.write(to_unicode(str_))

def create_native(item, file_name):
    with io.open(ABS_PATH + 'native/'+ file_name +'.txt','w', encoding='utf8') as tmpfile:
        str_ = json.dumps(item['content'], ensure_ascii=False)
        str_ = str_.replace('\\n', '\n')
        tmpfile.write(to_unicode(str_))

def create_loadfile(item, file_name):
    with open(ABS_PATH + 'loadfile.txt','a') as tmp_file:
        loadfile_list = attr_writer(item)
        #loadfile_list.append('"native/' + FILE_NAME + '.txt"')
        #loadfile_list.append('"text/' + FILE_NAME + '.txt"')
        #loadfile_list.append('"' +FILE_NAME + '.txt"')
        tmp_file.write(','.join(str(x) for x in loadfile_list) + '\r\n')

if __name__ == '__main__':
    param = sys.argv

    category = param[1]
    start = param[2]
    end = param[3]

    str_post_time = '2911/01/01 00:00:00'
    str_mod_time = '2911/01/01 00:00:00'
    str_agree = None
    str_disagree = None
    str_fence = None
    str_title = None
    str_author = None
    str_category = None
    #initialize_loadfile()
    initialize_loadfile_KP()

    try:
        conn = get_db()
        items = result_export(category, start, end)
        #print items.count()
        for i, item in enumerate(items):
            FILE_NAME = category + '_' + str(i)
            #create_text(item, FILE_NAME)
            #create_native(item, FILE_NAME)
            create_loadfile(item, FILE_NAME)

    except Exception as e:
        print 'Exception=%s' % e
        traceback.print_exc()

