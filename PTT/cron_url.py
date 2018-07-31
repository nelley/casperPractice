# -*- coding: utf-8 -*-
'''
getURL <board name>:
#getURL tech_job
#getURL salary
#getURL gossip
---------------------------
getContent <board name>:
#getContent tech_job
#getContent salary
#getContent gossip

┌───────────── minute (0 - 59)
 │ ┌───────────── hour (0 - 23)
 │ │ ┌───────────── day of month (1 - 31)
 │ │ │ ┌───────────── month (1 - 12)
 │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday;
 │ │ │ │ │                                       7 is also Sunday)
 │ │ │ │ │
 │ │ │ │ │
 * * * * *  command to execute

0 0 * * * every day in midnight
45 23 * * * every day in 23:45

'''
import sys
import os
from crontab import CronTab
import random
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

# init logger
logger = logging.getLogger('cron_url')
handler = RotatingFileHandler('/home/nelley/casperPractice/PTT/log_PTT_crawler.txt', maxBytes=1024*1024*5, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)

UPDATE_INTERVAL = 5 #hour
SPACE = ' '
CONTENT_CMD = '/usr/local/bin/casperjs'
CONTENT_PATH = '/home/nelley/casperPractice/PTT/crawl_content.js'

'''set the start time of crawl_content.js'''
def chain_crawl_content(u_cron, cate):
    logger.debug('start chain crawl content')
    content_cmt = cate + '_content' 
    #delete cron job
    u_cron.remove_all(comment=content_cmt)

    std = datetime.now().strftime('%H:%M')
    timeArr = std.split(':')

    new_min = int(timeArr[1]) + random.randint(5,10)
    new_hour = int(timeArr[0])

    if new_min > 59:
        new_min = str(new_min-60)
        new_hour = str(new_hour + 1)

    #create new cronjob
    chain_cmd = (CONTENT_CMD + SPACE 
                + CONTENT_PATH + SPACE 
                + '--category=\'' + cate + '\'' + SPACE 
                + '| python /home/nelley/casperPractice/PTT/update_content_Logs.py')

    new_job = user_cron.new(command=chain_cmd, 
                            comment=content_cmt)
    new_job.setall(new_min, new_hour,None,None,None)




def finished_in_exception():
    logger.debug('finished in exception  start')
    std = datetime.now().strftime('%H:%M')

    timeArr = std.split(':')

    #retry time interval 
    new_min = int(timeArr[1])+random.randint(5,15)
    new_hour = int(timeArr[0])
   
    if new_min > 59:
        new_min = str(new_min-60)
        new_hour = new_hour + 1
    if new_hour > 23:
        new_hour = str(0)
    return new_min, new_hour


'''
    if finished successfully, the crontab will set to 8 hours later
    from its started
'''
def finished_successfully(param):
    logger.debug('finished successfully start')
    
    #origin_param[0]:minutes
    #origin_param[1]:hour
    #origin_param[2]:day of month
    #origin_param[3]:month
    #origin_param[4]:day of week
    std_min = param[0] 
    std_hour = param[1]
    logger.debug('std hour:%s' % std_hour)
    logger.debug('std min:%s' % std_min)

    tmp_hour = int(std_hour) + UPDATE_INTERVAL 
    
    if tmp_hour > 23:
        std_hour = str((tmp_hour) - 24)
    else:
        std_hour = str(tmp_hour)
    
    std_min = str(random.randint(0,59))

    return std_min, std_hour    

'''
    arg1:comment write in cronjob
    arg2:category
    arg3:type of finish from crawler.js/ update_url.js

'''
if __name__ == "__main__":

    param = sys.argv
    comment = param[1]
    category = param[2]

    #type:0(finished successfully), 1(finished by exception)
    finish_type = param[3]

    logger.debug('comment:%s' % comment)
    logger.debug('finish type:%s' % finish_type) 

    user_cron = CronTab('root')

    origin_param = []

    job = user_cron.find_comment(comment)
    for item in job:
        logger.debug('cron job:' %  item)
        origin_param = str(item).split()

    logger.debug('cron job param array:%s' % origin_param)

    #delete cron job
    user_cron.remove_all(comment=comment)

    new_min='' 
    new_hour= ''

    if finish_type != '0':
        new_min, new_hour = finished_in_exception()
    else:
        new_min, new_hour = finished_successfully(origin_param)
        #chaining crawl_content.js
        chain_crawl_content(user_cron, comment)


    logger.debug('cron job param array:%s' % origin_param)
    #create new cronjob
    #origin_param[5]:command
    #origin_param[6]:execute file path
    cmd = (origin_param[5] + SPACE 
            + origin_param[6] + SPACE 
            + '--category=\'' + category + '\'' + SPACE 
            + '| python /home/nelley/casperPractice/PTT/update_Logs.py')

    new_job = user_cron.new(command=cmd, 
                        comment=comment)
    new_job.setall(new_min, new_hour,None,None,None)



    # save modification to cron
    user_cron.write_to_user('root')
    logger.debug('cron reconfig successed!')

