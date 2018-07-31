#-*- coding=utf-8 -*-
#######################cmd memo####################################
#>python chain.py -f foldername
#>python chain.py -refine visualize/DGdump_xxxxxxxx.json
#>python chain.py -m base_dict.txt diff_dict.txt
#
###################################################################

from __future__ import division
import os
import sys
import json
import datetime
import time
import codecs
import imp
import math
import re
import flask
import numpy
from numpy import *
import scipy.sparse as sp
from itertools import izip
from time import sleep
from random import shuffle
from collections import Counter
import networkx as nx
from networkx.readwrite import json_graph
from itertools import tee, islice, chain, izip
from argparse import ArgumentParser
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

import logging
from logging.handlers import RotatingFileHandler
ABS_PATH = '/home/nelley/casperPractice/PTT/mongoScript/' 

logging.basicConfig(level=logging.DEBUG)
# init logger
logger = logging.getLogger('chain')
handler = RotatingFileHandler(ABS_PATH +'log_chain.txt', maxBytes=1024*1024*5, backupCount=1)

fmt = logging.Formatter('[%(asctime)s %(msecs)d][%(name)s][%(levelname)s]: %(message)s',datefmt='%Y/%m/%d %H:%M:%S')
handler.setFormatter(fmt)

logger.addHandler(handler)


# パーサーを作る
parser = ArgumentParser(
    prog='Sentence Knife', # プログラム名
    usage='morphological analysis of traditional chinese\n 1.refine the json file\n 2.check the output file\n 3.merge to the dictionary', # プログラムの利用方法
    description='Jieba & Frequency Analysis Script', # 引数のヘルプの前に表示
    epilog='Current Ver.1.0 NELLEY 20180501', # 引数のヘルプの後で表示
    add_help=True, # -h/–help オプションの追加
)


#import package by full path
sys.path.insert(0, '/usr/local/lib/python3.4/site-packages')
import jieba
import jieba.analyse
jieba.set_dictionary(ABS_PATH + 'new_dict.txt')
jieba.enable_parallel(4)

re_han_default = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&\._%]+)", re.U)
DUMP_PATH = ABS_PATH + 'visualize/'

SOS = '<*>'
EOS = '</>'

START_AND_END = [SOS, EOS]


#====================================================================
#General Function start
#====================================================================
def representInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def add_html_tag(filename, t_ma, tokens, st, weight=0):
    """ add color opcity tag to the specific term
        t_ma = coo matrix
        tokens = term mapping list
        st = split term by jieba
    """
    visual_factor = 10
    zipped = {}
    #normalize the data value
    base = t_ma.sum(axis=0).sum(axis=1)
    ratio = 5/base
    print('ratio=%s' % ratio)
    #t_ma = t_ma.sum(axis=0)/t_ma.sum(axis=0).sum(axis=1)
    t_ma = t_ma.sum(axis=0)/base
    for idx,value in tokens.iteritems():
        zipped.setdefault(value.decode('utf-8'), t_ma[0, idx])
    
    #reconstruct the text with html tag
    filename = filename.replace('txt','html')
    r_html_tag = '<span style="background-color: rgba(255,0,0,'

    with open(ABS_PATH + 'visualize/output_html/' + filename, 'a') as outfile:
        for term in st:
            tmp_char = term[0]
            #print('ters: %s, %s' % (tmp_char, zipped.get(tmp_char,'None')))
            if tmp_char == '\n':
                outfile.write('<br>\n')

            elif tmp_char == ' ':
                outfile.write(tmp_char.encode('utf-8'))

            #elif tmp_char in term_set:
            elif zipped.get(tmp_char, 0) > ratio:
                #print('rendering: %s' % zipped.get(tmp_char))
                tmp_str = r_html_tag + str(zipped.get(tmp_char)*visual_factor)
                tmp_str += '); border-radius:25px">' + tmp_char.encode('utf-8')
                tmp_str += '</span>'
                outfile.write(tmp_str)

            else:
                outfile.write(tmp_char.encode('utf-8'))
        #logger.debug('%s þ %s þ %s þ %s' % (idx, tokens[pairs[1]], tokens[pairs[2]], pairs[3]))

def get_all_method(obj):
    print [method_name for method_name in dir(obj) if callable(getattr(obj, method_name))]

def get_dir_files(path):
    """ get all files from specific directory"""
    if os.path.isdir(path):
        return [path + x for x in os.listdir(ABS_PATH + path)]
    else:
        return [path]

def zh_stopword():
    FILE = '/home/nelley/casperPractice/PTT/mongoScript/idf_stop_word'
    sw_list = []

    f_sw = codecs.open(FILE, 'r', 'utf-8')
    for line in f_sw.readlines():
        term, tf = line.split(u'þ')
        sw_list.append(term)
    f_sw.close()
    return sw_list
    
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

def print_split_result(term):
    print '/'.join(x[0] for x in term)
    #sleep(2)


#====================================================================
#NetworkX Function start
#====================================================================
def weight_calc(type_list):
    """x+-2 window to calculate the serial dependency"""
    result = 0.0
    cnt = 0
    for idx, item in enumerate(type_list):
        if item != 'HMM':
            result = result + math.exp(cnt)
            #logger.debug('score=%s' % result)
            cnt -= 1
        else:
            #logger.debug('type=%s' % item)
            cnt = 0
    return result


def update_weight(current_word, total_length, idx):
    #logger.debug(current_word[idx][0])
    if idx == total_length - 1:
        #logger.debug('idx-4=%s, idx-3=%s, idx-2=%s, idx-1=%s, <<<idx=%s>>>' % (current_word[idx-4][0], current_word[idx-3][0], current_word[idx-2][0], current_word[idx-1][0], current_word[idx][0]))
        #logger.debug('idx-4=%s, idx-3=%s, idx-2=%s, idx-1=%s, <<<idx=%s>>>' % (current_word[idx-4][1], current_word[idx-3][1], current_word[idx-2][1], current_word[idx-1][1], current_word[idx][1]))
        return weight_calc([current_word[idx-4][1], current_word[idx-3][1], current_word[idx-2][1], current_word[idx-1][1], current_word[idx][1]])

    elif idx == total_length - 2 :
        #logger.debug('idx-3=%s, idx-2=%s, idx-1=%s, <<<idx=%s>>>, idx+1=%s' % (current_word[idx-3][0], current_word[idx-2][0], current_word[idx-1][0], current_word[idx][0], current_word[idx+1][0]))
        #logger.debug('idx-3=%s, idx-2=%s, idx-1=%s, <<<idx=%s>>>, idx+1=%s' % (current_word[idx-3][1], current_word[idx-2][1], current_word[idx-1][1], current_word[idx][1], current_word[idx+1][1]))
        return weight_calc([current_word[idx-3][1], current_word[idx-2][1], current_word[idx-1][1], current_word[idx][1], current_word[idx+1][1]])

    elif idx == 0:
        #logger.debug('<<<idx=%s>>>, idx+1=%s, idx+2=%s, idx+3=%s, idx+4=%s' % (current_word[idx][0], current_word[idx+1][0], current_word[idx+2][0], current_word[idx+3][0], current_word[idx+4][0]))
        #logger.debug('<<<idx=%s>>>, idx+1=%s, idx+2=%s, idx+3=%s, idx+4=%s' % (current_word[idx][1], current_word[idx+1][1], current_word[idx+2][1], current_word[idx+3][1], current_word[idx+4][1]))
        return weight_calc([current_word[idx][1], current_word[idx+1][1], current_word[idx+2][1], current_word[idx+3][1], current_word[idx+4][1]])

    elif idx == 1:
        #logger.debug('idx-1=%s, <<<idx=%s>>>, idx+1=%s, idx+2=%s, idx+3=%s' % (current_word[idx-1][0], current_word[idx][0], current_word[idx+1][0], current_word[idx+2][0], current_word[idx+3][0]))
        #logger.debug('idx-1=%s, <<<idx=%s>>>, idx+1=%s, idx+2=%s, idx+3=%s' % (current_word[idx-1][1], current_word[idx][1], current_word[idx+1][1], current_word[idx+2][1], current_word[idx+3][1]))
        return weight_calc([current_word[idx-1][1], current_word[idx][1], current_word[idx+1][1], current_word[idx+2][1], current_word[idx+3][1]])

    else:
        #logger.debug('idx-2=%s, idx-1=%s, <<<idx=%s>>>, idx+1=%s, idx+2=%s' % (current_word[idx-2][0], current_word[idx-1][0], current_word[idx][0], current_word[idx+1][0], current_word[idx+2][0]))
        #logger.debug('idx-2=%s, idx-1=%s, <<<idx=%s>>>, idx+1=%s, idx+2=%s' % (current_word[idx-2][1], current_word[idx-1][1], current_word[idx][1], current_word[idx+1][1], current_word[idx+2][1]))
        return weight_calc([current_word[idx-2][1], current_word[idx-1][1], current_word[idx][1], current_word[idx+1][1], current_word[idx+2][1]])


def add_char(G, sentence, print_flag=0):
    #pre_word = '<*>'
    pre_word = SOS

    split_word =  list(jieba.cut(sentence, cut_all=False))

    if print_flag:
        print_split_result(split_word)

    length = len(split_word)

    if length < 5:
        #logger.debug('Skipped=%s' % split_word[0][0])
        return None

    #for word in split_word:
    for idx in xrange(0, length):
        #logger.debug('word from jieba=%s, %s, pre_word=%s' % (word[0],word[1], pre_word))
        found_in_pool = False

        for n, attr in G.nodes_iter(data=True):
            if attr:
                #print('MATCH OR NOT? n=%s, word[0]=%s' % (n,word[0]))
                if n == split_word[idx][0]:
                    G.node[n]['counter'] += 1
                    found_in_pool = True
                    #print('add edge s=%s, e=%s' % (pre_word, n))

                    cal_weight = update_weight(split_word, length, idx)
                    G.add_edge(pre_word, n, weight = cal_weight)
                    break
                else:
                    #print('found in pool False')
                    found_in_pool = False

        if not found_in_pool:
            G.add_node(split_word[idx][0], {'predicType':split_word[idx][1], 'counter':1})
            #print('add edge s=%s, e=%s' % (pre_word, n))

            cal_weight = update_weight(split_word, length, idx)
            G.add_edge(pre_word, split_word[idx][0], weight = cal_weight)
            #print('word[0] added=%s' % word[0])
        pre_word = split_word[idx][0]
        #print('=====================================')
    G.add_edge(split_word[idx][0], EOS)



def get_all_path(G, start=SOS, end=EOS):
    #get all path(not include cycle node)
    for path in nx.all_simple_paths(G, source=start, target=end):
        logger.debug('/'.join(path))

def get_all_edges(G):
    for x in G.edges_iter(data=True):
        logger.debug('edge start=%s end=%s weight=%s' % x)

def get_all_nodes(G):
    for n, attr in G.nodes_iter(data=True):
        if attr:
            logger.debug('node=%s, attr=%s' %  (n,attr))


def cal_node_weight(G):
    '''
    calculate the avg of all connection of a node
    '''
    total_mean = 0.0
    cnt = 0

    for n, attr in G.nodes_iter(data=True):
        if attr and not any(n in s for s in START_AND_END):
            tmp = 0.0
            for edge in G.in_edges_iter(n ,data=True):
                #check key 'weight' in the dict
                if 'weight' in edge[2]:
                    tmp += edge[2]['weight']
            #print('n=%s, tmp=%s, avg=%s' % (n, tmp, (tmp/len(G.in_edges(n)))))
            #print('node=%s, type=%s' % (G.node[n],type(G.node[n])))

            if len(G.in_edges(n)):
                G.node[n]['updated_weight'] = (tmp/len(G.in_edges(n)))
            else:
                G.node[n]['updated_weight'] = -1 
                
            cnt += 1
            total_mean += tmp
    logger.debug('score_sum=%s, count=%s' % (total_mean, cnt))
    return (total_mean, cnt)


def show_predict(G):
    # get mean weight of the HMM nodes
    for n, attr in G.nodes_iter(data=True):
        if attr and attr['predicType'] == 'HMM':
            print('%s, %s' % (n, attr))

def aging(G, aging_std=1):
    '''remove node by count'''
    #black list creation
    for n, attr in G.nodes_iter(data=True):
        if attr and attr['counter'] <= aging_std and not any(n in s for s in START_AND_END):
            G.remove_node(n)
            #add to black list

    print('std=%s, affter aging=%s' % (aging_std, len(G)))

def create_in_iter(G):
    '''process all files in the specific folder'''
    SAVE_TO_FILE_CYCLE = 1500
    AGING_STD = 100
    file_cnt = 0 
    
    fileNameList = os.listdir(_dir_name_)
    shuffle(fileNameList)

    for filename in fileNameList:
        if filename.endswith('txt'):
            s_time = time.time()
            logger.debug('filename=%s start process' % filename)
            tmp_file = codecs.open(_dir_name_ + filename, 'r', 'utf-8')
            content = tmp_file.read()

            content = clean_by_regex(content)
            blocks = re_han_default.split(content)
            for blk in blocks:
                #logger.debug('<<<blk=%s>>>' % blk)
                add_char(G, blk)

            if (file_cnt % AGING_STD) == 0 and file_cnt != 0:
                aging(G, (file_cnt/AGING_STD))

            if (file_cnt % SAVE_TO_FILE_CYCLE) == 0 and file_cnt != 0:
                serialize(G)

            tmp_file.close()

        file_cnt += 1
        logger.debug('%s file with %s nodes, filename=%s END process, Processed Time:%0.2f sec' % (file_cnt, len(G), filename, time.time() - s_time))

    aging(G)

def serialize(G):
    total_score, word_cnt = cal_node_weight(G)

    now = datetime.datetime.now()

    stored_G = json_graph.node_link_data(G)
    with open(DUMP_PATH + 'DGdump_' + now.strftime('%Y%m%d%H%M%S') + '.json', 'w') as outfile:
        jsonobj = json.dump(stored_G, outfile)


def deserialize(filename):
    '''read stored trie for processing'''
    with open(ABS_PATH + filename, 'r') as infile:
        datarestore = json.load(infile)
        return json_graph.node_link_graph(datarestore)


def predicted_by_param(G, length=0, count=1, weight=1):
    '''write candidate word to the dict'''
    CANDIDATE_THRESHOLD = 0.01
    try:
        with open(ABS_PATH + 'predict_dict.txt', 'w') as outfile:
            for n, attr in G.nodes_iter(data=True):
                #if attr and attr['predicType'] == 'HMM' and (attr['counter']/word_count) > CANDIDATE_THRESHOLD:
                if attr and attr['predicType'] == 'HMM' and len(n)>length-1 and attr['counter']>count:
                    if attr['updated_weight'] > weight:
                        outfile.write(n.encode('utf-8') + ' ' + str(attr['counter']) + '\n')
        logger.debug('<<<predict_dict.txt is made!!!>>>')
    except Exception, e:
        logger.debug('ERROR:%s\n , %s, %s, in_edges=%s' % (e,n,attr,G.in_edges(n)))


def merge_to_dict(base, diff):
    '''
    merge predicted one to the base dict
    load the txt to two dict, after merging two dict,
    sum up the value(count) if the key is the same
    '''
    new_word_flag = 1 
    exist_dict={}
    candidate={}

    with open(ABS_PATH + diff, 'r') as pd:
        for line in pd:
            key = line.split()[0]
            val = int(line.split()[1])
            candidate[key]=val

    with open(ABS_PATH + base, 'r') as dp:
        for line in dp:
            key = line.split()[0]
            val = int(line.split()[1])
            exist_dict[key]=val

    tmp = Counter(candidate) + Counter(exist_dict)

    with open(ABS_PATH + 'new_dict.txt', 'w') as nf:
        for key, ele in tmp.iteritems():
            nf.write('%s %s\n' % (key, ele))

    logger.debug('Before:[%s] Words, After=[%s] Words, <%s> Words Added' % (len(exist_dict), len(tmp), (len(tmp)-len(exist_dict))))

def get_dict_difference(dict1_path, dict2_path):
    base = {}
    diff = {}
    
    with open(dict1_path, 'r') as d1:
        for line in d1:
            key = line.split()[0]
            val = int(line.split()[1])
            base[key] = val

    with open(dict2_path, 'r') as d2:
        for line in d2:
            key = line.split()[0]
            val = int(line.split()[1])
            diff[key] = val

    value = {k: diff[k] for k in set(diff) - set(base)}
    
    with open(ABS_PATH + 'diff_dict.txt', 'w') as df:
        for key, ele in value.iteritems():
            df.write('%s %s\n' % (key, ele))

    logger.debug('<%s> Diff Words Recognized, diff_dict.txt is made!!!' % (len(value)))

#====================================================================
#Visualization Function start
#====================================================================
def serverStart():
    # Serve the file over http to allow for cross origin requests
    app = flask.Flask(__name__, static_folder="visualize")

    @app.route('/<path:path>')
    def static_proxy(path):
        return app.send_static_file(path)

    print('\nGo to http://127.0.0.1:8000/index.html to see the example\n')
    app.run(port=8000)


#====================================================================
#Matrix Calc Function start
#====================================================================
def create_coo_matrix(path):
    """create coo matrix from jieba's token
       (doc_cnt,j)= (doc_no, term count)
    """

    mapping_dict = {}
    vocabulary={}
    data=[]
    row=[]
    col=[]
    doc_cnt = 0

    files = get_dir_files(path)
    for fs in files:
        #logger.debug('File Loaded:%s' % ABS_PATH + path + fs)
        logger.debug('File Loaded:%s' % fs)
        outfile = codecs.open(fs,  'r', 'utf-8')

        read_string = outfile.read()
        # filtered by regex
        read_string = clean_by_regex(read_string)
        tokens = list(jieba.cut(read_string, cut_all=False))
        for tk in tokens:
            j=vocabulary.setdefault(tk[0].encode('utf-8'),len(vocabulary))
            mapping_dict.setdefault(j, tk[0].encode('utf-8'))

            data.append(1.); row.append(doc_cnt); col.append(j);

        doc_cnt += 1


    coo_m = sp.coo_matrix((data,(row,col)))

    #for i in xrange(len(str_list)):
    #    tokens = list(jieba.cut(str_list[i], cut_all=False))
    #    for tk in tokens:
    #        vo_size = len(vocabulary)
    #        j=vocabulary.setdefault(tk[0].encode('utf-8'),len(vocabulary))
    #        data.append(1.); row.append(i); col.append(j);

    #coo_m = sp.coo_matrix((data,(row,col)))
    return coo_m, mapping_dict, doc_cnt

def iter_coocur_matrix(coo_matrix, tokens, doc_id=[]):
    """print cooccurrence_calc func's output"""
    #iterate in index mode
    zipped = zip(doc_id, coo_matrix.row, coo_matrix.col, coo_matrix.data)
    zipped.sort(key = lambda t:t[3], reverse=False)
    for pairs in zipped:
        print("Doc_id=%s:(<%s>,<%s>)=%s" % (pairs[0], tokens[pairs[1]], tokens[pairs[2]],pairs[3]))



def cooccurrence_calc(files):
    """共起を計算するメソッド
    """
    #co-occurence
    WINDOW_SIZE = 1 
    sw_list = zh_stopword()

    for fs in files:
        mapping_dict = {}
        vocabulary={}
        data=[]
        row=[]
        col=[]

        outfile = codecs.open(fs,  'r', 'utf-8')
        read_string = outfile.read()
        #recons_tks for reconstructing whole paragraph
        recons_tks = list(jieba.cut(read_string, cut_all=False))

        read_string = clean_by_regex(read_string)
        tokens = list(jieba.cut(read_string, cut_all=False))

        for pos,token in enumerate(tokens):
            # check key is existed or not. if existed, return the key value(pos info). ex: {'我':0, '是':1}
            i=vocabulary.setdefault(token[0].encode('utf-8'),len(vocabulary))
            mapping_dict.setdefault(i, token[0].encode('utf-8'))

            start=max(0,pos-WINDOW_SIZE)
            end=min(len(tokens),pos+WINDOW_SIZE+1)

            for pos2 in xrange(start,end):
                #如果要做windows是本身or特殊符號/感嘆詞等,跳過處理(但可經由其他詞與特殊符號做連結)
                if pos2==pos or tokens[pos2][0] in sw_list:
                    continue
                #logger.debug('token[%s][0]=%s' % (pos2,tokens[pos2][0]))
                j=vocabulary.setdefault(tokens[pos2][0].encode('utf-8'),len(vocabulary))
                data.append(1.); row.append(i); col.append(j);

        coo_m = sp.coo_matrix((data,(row,col)))
        coo_m.sum_duplicates()
        coo_m = sp.triu(coo_m, k=1) #get upper triangle
        yield(fs, coo_m, mapping_dict, recons_tks)

 
def TF_calc(m, tks):
    """ result of calc DOES NOT normalized
        normalized = (coo_m.todense()/coo_m.sum(axis=1))
    """
    zipped = zip(m.row, m.col, m.data)
    zipped.sort(key = lambda t:t[2], reverse=False)
    for pairs in zipped:
        print("(doc_No<%s>, term<%s>)=%s" % (pairs[0],tks[pairs[1]],pairs[2]))
 

def IDF(coo_matrix, tokens, doc_size):
    """ calculate IDF value by coo matrix
        closer to 1.0 means shown almost to every doc
    """
    dedup = set()
    data2 = []
    row2 = []
    col2 = []
    for i,j,v in zip(coo_matrix.row, coo_matrix.col, coo_matrix.data):
        dedup.add('%s,%s,%s' % (i,j,v))
    for item in list(dedup):
        t_row, t_col, t_data = item.split(',')
        data2.append(float(t_data)); row2.append(int(t_row)); col2.append(int(t_col))
    deduped_coo_m = sp.coo_matrix((data2,(row2,col2)))

    idf_matrix = (deduped_coo_m.sum(axis=0)/doc_size).tolist()

    zipped = zip(list(tokens.values()), idf_matrix[0])
    zipped.sort(key = lambda t:t[1], reverse=True)
    for z in zipped:
        print('Term=%s, IDF=%s' % (z[0], z[1]))

def mutual_information(target, data, k=0):
    """カテゴリtargetにおける相互情報量が高い上位k件の単語を返す"""
    # 上位k件を指定しないときはすべて返す
    if k == 0: k = sys.maxint
 
    V = set()
    N11 = defaultdict(float)  # N11[word] -> wordを含むtargetの文書数
    N10 = defaultdict(float)  # N10[word] -> wordを含むtarget以外の文書数
    N01 = defaultdict(float)  # N01[word] -> wordを含まないtargetの文書数
    N00 = defaultdict(float)  # N00[word] -> wordを含まないtarget以外の文書数
    Np = 0.0  # targetの文書数
    Nn = 0.0  # target以外の文書す
    
    # N11とN10をカウント
    for d in data:
        cat, words = d[0], d[1:]
        #print('%s, %s' % (d[0],d[1:]))
        if cat == target:
            Np += 1
            for wc in words:
                word, count = wc.split(":")
                V.add(word)
                N11[word] += 1  # 文書数をカウントするので+1すればOK
        elif cat != target:
            Nn += 1
            for wc in words:
                word, count = wc.split(":")
                V.add(word)
                N10[word] += 1
    
    # N01とN00は簡単に求められる
    for word in V:
        N01[word] = Np - N11[word]
        N00[word] = Nn - N10[word]
    # 総文書数
    N = Np + Nn
    
    # 各単語の相互情報量を計算
    MI = []
    for word in V:
        n11, n10, n01, n00 = N11[word], N10[word], N01[word], N00[word]
        if word == u'台積電' or word == u'預計':
            print('word=%s, n11=%s, n10=%s, n01=%s, n00=%s' % (word, n11, n10, n01, n00))
        # いずれかの出現頻度が0.0となる単語はlog2(0)となってしまうのでスコア0とする
        if n11 == 0.0 or n10 == 0.0 or n01 == 0.0 or n00 == 0.0:
            MI.append( (0.0, word) )
            continue
        # 相互情報量の定義の各項を計算
        temp1 = n11/N * math.log((N*n11)/((n10+n11)*(n01+n11)), 2)
        temp2 = n01/N * math.log((N*n01)/((n00+n01)*(n01+n11)), 2)
        temp3 = n10/N * math.log((N*n10)/((n10+n11)*(n00+n10)), 2)
        temp4 = n00/N * math.log((N*n00)/((n00+n01)*(n00+n10)), 2)
        score = temp1 + temp2 + temp3 + temp4
        MI.append( (score, word) )
    
    # 相互情報量の降順にソートして上位k個を返す
    MI.sort(reverse=True)
    return MI[0:k]


if __name__ == '__main__':
    logger.debug('=============================================================')
    parser.add_argument('-m', '--merge', nargs='*', help='merge mode')
    parser.add_argument('-f', '--folder', help='process whole folder mode')
    parser.add_argument('-v', '--visualize', help='start d3.js')
    parser.add_argument('-dev', '--dev', help='dev mode')
    parser.add_argument('-dev_tmp', '--dev_tmp', help='dev mode')
    parser.add_argument('-sf', '--sf', help='single file mode')
    parser.add_argument('-diff', '--get_diff', nargs='*', help='get difference mode')
    parser.add_argument('-refine', '--refine', help='reproduce predicted dictionary by different param')
    parser.add_argument('-tfidf', '--tfidf', help='calculate tfidf of all files in the given folder')
    parser.add_argument('-tfidf_html', '--tfidf_html', help='tfidf visualization')
    parser.add_argument('-mui', '--mui', help='mutual information calculation')
    parser.add_argument('-tf', '--tf', help='TF calc(made by self)')
    parser.add_argument('-idf', '--idf', help='IDF calc(made by self)')
    parser.add_argument('-cooc', '--cooc', help='cooccurrence calc(made by self)')
    args = parser.parse_args()
    
    _dir_name_ = args.folder

    #######################################
    # initialize 
    #######################################
    start_time = time.time()
    G = nx.DiGraph()
    G.add_node(SOS, {'predicType':u'root', 'counter':0})
    G.add_node(EOS, {'predicType':u'end', 'counter':0})


    #######################################
    # bulk process by folder 
    #######################################
    if _dir_name_:
        create_in_iter(G)
        print('============================')
    #get_all_method(G)
    
    #######################################
    # mutual information calculation text generation 
    #######################################
    if args.mui:
        #calculate TF of each doc
        _dir_name_ = '/home/nelley/casperPractice/PTT/mongoScript/shiken/score/home-sale/'
        #_dir_name_ = '/home/nelley/casperPractice/PTT/mongoScript/shiken/score/movie/'
        #_dir_name_ = '/home/nelley/casperPractice/PTT/mongoScript/shiken/score/tech_job/'
        for filename in os.listdir(_dir_name_):
            if filename.endswith('txt'):
                logger.debug('filename=%s start process' % filename)
                tmp_file = codecs.open(_dir_name_ + filename, 'r', 'utf-8')
                content = tmp_file.read()

                content = clean_by_regex(content)
                blocks = re_han_default.split(content)

                for blk in blocks:
                    add_char(G, blk, 0)

                tmp_file.close()

            #get_all_nodes & write to the output files
            with open('/home/nelley/casperPractice/PTT/mongoScript/shiken/score/Cat_TF','a') as outfile:
                #load zh stop word list
                sw_list = zh_stopword()
                outfile.write(args.mui + ' ')
                for n, attr in G.nodes_iter(data=True):
                    if attr and attr['predicType'] != 'punc':
                        if n not in sw_list and n not in START_AND_END:
                            outfile.write(n.encode('utf-8') + ':' + str(attr['counter']))
                            outfile.write(' ')
                            #logger.debug('node=%s, attr=%s' %  (n,attr))
                            #logger.debug('node=%s, attr=%s' %  (n,attr['counter']))
                outfile.write('\n')
            G.clear()

    #######################################
    # dev mode 
    #######################################
    if args.dev:
        #add_char(G, '宅男澎湖灣看海的日子,很愜意', 1)
        #add_char(G, '愛在澎湖,是一部台灣少有的深度電影', 1)
        #add_char(G, '澎湖灣有雙心石滬,有很多爸媽帶小孩去玩', 1)
        #add_char(G, '我愛在家裡洗澡,因為家裡的衛浴設備很好,他就不喜歡了', 1)
        #add_char(G, '海灣地形在台灣很常見,不過多數在東部', 1)
        #get_all_edges(G)
        #get_all_nodes(G)

        sample=[u'我是一個學生,但我也是一個台灣人', u'台灣是一個好地方', u'我愛台灣', u'他']


    if args.dev_tmp:
        from collections import defaultdict
        # 訓練データをロード
        trainData = []
        #fp = codecs.open("news20_bk", "r", "utf-8")
        fp = codecs.open("shiken/score/Cat_TF", "r", "utf-8")
        '''output is enfluenced by 有該關鍵字的文件數, 文件數越高該關鍵字的特徵值越高'''
        '''反而關鍵字在文件裡面出現的頻率不會有影響'''
        for line in fp:
            line = line.rstrip()
            temp = line.split()
            trainData.append(temp)
        fp.close()

        # 相互情報量を用いて特徴選択
        target = args.dev_tmp
        features = mutual_information(target, trainData, k=30)
        print "[%s]" % target
        for score, word in features:
            print score, word

    #######################################
    # sklearn TFIDF & TFIDF visualize 
    #######################################
    if args.tfidf:
        file_list = []          #input for TFIDF
        file_name_list = []     #for mapping TFIDF to text file
        split_word_list = []    #for mapping terms of each text

        fName_List = os.listdir(args.tfidf)
        for fs in fName_List:
            logger.debug('File Loaded:%s' % ABS_PATH + args.tfidf + fs)
            outfile = codecs.open(ABS_PATH + args.tfidf + fs,  'r', 'utf-8')

            read_string = outfile.read()
            # filtered by regex
            read_string = clean_by_regex(read_string)
            split_word = list(jieba.cut(read_string, cut_all=False))
            split_string = ''

            #for x in split_word:
            #    if not re.search(r'\d', x[0]):  #get rid of number by regex
            #        split_string += x[0]

            #connect by space from jieba's output
            split_string = ' '.join(x[0] for x in split_word)
            #logger.debug(split_string)

            #append to list as a text
            file_list.append(split_string)
            file_name_list.append(fs)
            split_word_list.append(list(set(split_word)))
            outfile.close()

        vectorizer = CountVectorizer(max_df=0.8)
        transformer = TfidfTransformer()
        vc_transform = vectorizer.fit_transform(file_list)
        TFIDF = transformer.fit_transform(vc_transform)
        words = vectorizer.get_feature_names()  #total words of n texts
        weight = TFIDF.toarray()                # text x word weights matrix

        key = vectorizer.get_feature_names()
        value = vc_transform.toarray().sum(axis=0)
        final = dict(zip(key,value))
        for idx,v in enumerate(final):
            print('k=%s, v=%s' % (v.encode('utf-8'),final[v]))


        for i in range(len(weight)):
            zipped = zip(weight[i], words)
            zipped.sort(key = lambda t:t[0], reverse=True)
            #open the file for writing the TFIDF
            #with open(ABS_PATH + 'for_movie/tfidf/' + file_name_list[i], 'w') as outfile:
            with open(ABS_PATH + args.tfidf + 'tfidf_' + file_name_list[i], 'w') as outfile:
                logger.debug('writing file:%s' % file_name_list[i])
                for z in zipped:                                    #loop all words come from TFIDF
                    #for sw in split_word_list[i]:                   #loop all words come from text
                    #    if sw[0] == z[1]:                           #only write the words in the specific text
                    outfile.write('%s,%s\n' % (z[1].encode('utf-8'),z[0]))
   
    
    if args.tfidf_html:
        # visualize with html
        TFIDF_item = []
        text_content = ''

        #open the TFIDF of each text
        for fs in os.listdir('/home/nelley/casperPractice/PTT/mongoScript/for_test/tfidf'):
            #outfile = codecs.open(ABS_PATH + 'for_test/tfidf/' + fs, 'r', 'utf-8')
            outfile = codecs.open(ABS_PATH + 'for_test/tfidf/tech_job_41.txt', 'r', 'utf-8')
            TFIDF_item = outfile.read().split('\n')
            outfile.close()

            #outfile = codecs.open(ABS_PATH + 'for_test/text/' + fs, 'r', 'utf-8')
            outfile = codecs.open(ABS_PATH + 'for_test/text/tech_job_41.txt', 'r', 'utf-8')
            text_content = outfile.read()
            outfile.close()

            for item in TFIDF_item:
                if item:
                    split_item = item.split(',')[0]
                    split_weight = item.split(',')[1]
                    if not representInt(split_item) and not split_item == '':
                        html_tag = '<span style="background-color: rgba(255,0,0,' + split_weight + ')">'
                        html_tag = html_tag + split_item + '</span>'
                        #html_tag = html_tag.replace('OPACITY', split_weight)
                        #html_tag = html_tag.replace('TFIDF_WORD', split_item)
                        text_content = text_content.replace(split_item, html_tag)
                        #print(text_content)
                        #sleep(1)
            fn = fs.replace('txt', 'html')
            with open(ABS_PATH + 'visualize/output_html/' + fn, 'w') as outfile:
                outfile.write(text_content.encode('utf-8'))

       
    #######################################
    # dev single text file mode 
    #######################################
    if args.sf:
        with open(ABS_PATH + args.sf) as outfile:
            for line in outfile:
                add_char(G, line, 1) 
        #get_all_nodes(G)
        print('============================')


    #######################################
    # merge mode 
    #######################################
    if args.merge:
        _base_ = args.merge[0]
        _diff_ = args.merge[1]
        merge_to_dict(_base_, _diff_)

    #######################################
    # get difference mode 
    #######################################
    if args.get_diff:
        _base_file = args.get_diff[0]
        _diff_file = args.get_diff[1]
        get_dict_difference(ABS_PATH + _base_file, ABS_PATH + _diff_file)

    
    #######################################
    # refine area
    #######################################
    if args.refine:
        restored_G = deserialize(args.refine)
        predicted_by_param(restored_G, length=2, count=0, weight=0.0)
    
    #######################################
    # TF calculation
    #######################################
    if args.tf:
        coo_m, tokens, doc_size= create_coo_matrix(args.tf)
        coo_m.sum_duplicates()
        coo_m = sp.triu(coo_m, k=1) #get upper triangle
        TF_calc(coo_m, tokens)
 

    #######################################
    # IDF calculation
    #######################################
    if args.idf:
        coo_m, tokens, doc_size= create_coo_matrix(args.idf)
        coo_m.sum_duplicates()
        coo_m = sp.triu(coo_m, k=1) #get upper triangle
        IDF(coo_m, tokens, doc_size)

    #######################################
    # cooccurrence calculation
    #######################################
    if args.cooc:
        files = get_dir_files(args.cooc)
        #iter_coocur_matrix(coo_m, tokens, doc_id)
        for fs, coo_m, tokens, split_t in cooccurrence_calc(files):
            add_html_tag(fs, coo_m, tokens, split_t, 1)

    #arg1:start, arg2:end
    #G.add_edge('nelley','candy',  weight=10)

    logger.debug('============================')
    print('Processed Time:%0.2f seconds' % (time.time() - start_time))

    logger.debug('============================')
    #######################################
    # show the node attribute
    #print(G.node[u'灣看']['counter'])
    #print(G.node)
    #get_all_path(G)
    #show_predict(G)
    #
    #show the next node
    #print(G['nelley'])
    #######################################


    #######################################
    # start server and check the d3.js graph 
    #######################################
    if args.visualize:
        # d3.js
        total_score, word_cnt = cal_node_weight(G)

        stored_G = json_graph.node_link_data(G)
        with open(DUMP_PATH + 'DGdump.json', 'w') as outfile:
            jsonobj = json.dump(stored_G, outfile)

        serverStart()


