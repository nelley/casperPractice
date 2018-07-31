# -*- coding: utf-8 -*-

# Using for remove html tags and
# extract necessary part for mecab

from bs4 import BeautifulSoup
import bs4
import urllib2
import sys
import os
import csv
import re
import psycopg2
from shutil import copyfile
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from mongo_driver import *
import json
import dateutil.parser
import pdb



pdb.set_trace()

#SAVE_PATH = '/home/nelley/casperPractice/PTT/mecab_' + datetime.now().strftime('%Y%m%d') + '/'

REG_PUSH = u'\u63a8\s+\w+:\s+.+\n'
REG_ARROW = u'\u2192\s+\w+:\s+.+\n'
REG_SUCK = u'\u5653\s+\w+:\s+.+\n'
#\\u63a8\s+\w+:(.)+\\n

invalid_tags = ['html', 'body', 'head', 'title',  'iframe', 'div', 'span', 'link', 'a', 'meta']
AUTHOR_ptt = u'作者'
CREATETIME_ptt = u'時間'
TITLE_ptt = u'標題'
NEGATIVE_ptt= u'噓'

# init logger
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('pttParser_dev')
handler = RotatingFileHandler('/home/nelley/casperPractice/PTT/dev/log_pttParser_dev.txt', maxBytes=1024*1024*5, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)

'''insert streaming logs into db'''
def updateLog(c, logs):
    
    conn = get_db()
    #logger.debug(logs) 
    conn.update_content_Logs.insert({'category':c, 
                                     'logs':logs['logs'],
                                     'date':datetime.now().strftime('%Y/%m/%d %H:%M:%S')})


'''function to detect 404 not found page'''
def is_404(s, c, u):
    for i in s.findAll('div', {'class', 'bbs-screen bbs-content'}):
        if '404 - Not Found.' in ''.join(i.findAll(text=True)).encode('utf8'):
            # update 404 not found to URL_list collection
            try:
                logger.debug('update 404 not found to URL_list:%s' % u)
                conn = get_db()
                conn.URL_list.update({'category':c, 'url':u},
                                    {'$set':{'is_deleted':True}})

            except Exception as e:
                logger.debug('exception happened when update 404 not found')

            return True
        else:
            return False



''' author, nickname,  title, createdate'''
def get_meta(s):
    logger.debug('get meta start')
    author_nickname = ''
    time = ''
    title = ''
    
    logger.debug('start extration') 
    # iterate article-metaline to get author, createtime, title
    for i in s.findAll('div', {"class", "article-metaline"}):
        for k in i.findAll('span', {"class":"article-meta-tag"}):
            if (''.join(k.findAll(text=True)).encode('utf8') == AUTHOR_ptt.encode('utf8')):
                for k in i.findAll('span', {"class":"article-meta-value"}):
                    author_nickname =  ''.join(k.findAll(text=True)).encode('utf8')
            elif(''.join(k.findAll(text=True)).encode('utf8') == CREATETIME_ptt.encode('utf8')):
                for k in i.findAll('span', {"class":"article-meta-value"}):
                    try:
                        date_object = datetime.strptime(''.join(k.findAll(text=True)), '%a %b %d %H:%M:%S %Y')
                        #time =  date_object.strftime('%Y/%m/%d %H:%M:%S')
                        time = dateutil.parser.parse(date_object.strftime('%Y-%m-%dT%H:%M:%S.000Z'))
                    except ValueError:
                        time = dateutil.parser.parse('1985-04-05T15:29:05.000Z')

            elif(''.join(k.findAll(text=True)).encode('utf8') == TITLE_ptt.encode('utf8')):
                for k in i.findAll('span', {"class":"article-meta-value"}):
                    title =  ''.join(k.findAll(text=True)).encode('utf8')

    logger.debug('extration finished') 
    # author and nickname is combined in one tag, so here is the seperating task
    author = re.sub("(\(.+\)|\(\))", '', author_nickname)    #replace space to nickname & brackets(extract author)
    nickname = re.search("\((.+)\)", author_nickname)   #extract nickname

    if nickname:
        nickname =  nickname.group(1)
    else:
        nickname = 'No Nickname'

    logger.debug('get meta finished')
    return author, nickname, title, time


'''get agree, disagree, fence total count'''
def get_push_class_cnt(s):
    logger.debug('get push class count start')
    push_tag =s.findAll('span',{"class":"f1 hl push-tag"})
    agree_cnt = 0
    disagree_cnt = 0
    fence_cnt = 0

    # iterate all(except agree) to seperate disagree & fence
    for item in push_tag:
        if (''.join(item.findAll(text=True)).encode('utf8').strip() == NEGATIVE_ptt.encode('utf8')):
            disagree_cnt+=1

    total = len(s.findAll('div', {"class", "push"}))

    agree_cnt = total-len(push_tag)
    fence_cnt = len(push_tag) - disagree_cnt

    logger.debug('get push class count end')
    return agree_cnt, disagree_cnt, fence_cnt

'''function for remove HTML tags'''
def removeHTML(content, url, category):
    logger.debug('removeHTML start, url:%s' % url)
    soup = BeautifulSoup(content, "html.parser")
 
    logger.debug('extract html contents by tag')

    # get each column for insert to DB
    author_ptt , nickname_ptt, title_ptt, time_ptt = get_meta(soup)
    agree, disagree, fence = get_push_class_cnt(soup)
    print 'author=%s, nickname=%s, title=%s, time_ptt=%s' % (author_ptt, nickname_ptt, title_ptt, time_ptt)

    logger.debug('extact contents finished')

    # remove all by id
    for div in soup.find_all("div", {'id':'topbar-container'}): 
        div.decompose()

    for div in soup.find_all("div", {'id':'navigation-container'}): 
        div.decompose()

    #remove push msg time
    for div in soup.find_all("span", {'class':'push-ipdatetime'}): 
        div.decompose()

    logger.debug('decompose finished')

    # remove all by tag
    [item.extract() for item in soup.contents if isinstance(item, bs4.Doctype)]
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]

    # replace push class to \n
    for div in soup.find_all("div", {'class':'push'}):
        div.replaceWith('%s\n' % div.text)

    for tag in invalid_tags: 
        for match in soup.findAll(tag):
            match.replaceWithChildren()


    html = "".join(line.strip() for line in str(soup).split("\n"))
    
     
    #result = re.split('(' + REG_PUSH + '|' + REG_ARROW + '|' + REG_SUCK + ')', html)
    #result = list(filter(None, result))
    #print result
    #for x in result:
    #    print 'x=%s' % x
    #    print '------------------'
    
    logger.debug('html rendering finished')
    logger.debug('removeHTML finished')


if __name__ == "__main__":
    logger.debug('main start')
    param = sys.argv
 
    # arg1-arg(n): seperated content with html tags
    # arg(-3):url
    # arg(-2):category
    # arg(-1):log come from crawl_content.js

    test_content = ''
    with open ('test_data_ptt_html.txt','r') as myfile:
        test_content = myfile.read()
    
    removeHTML(test_content, '/bbs/Gossiping/M.1488298984.A.E75.html', 'gossip')



