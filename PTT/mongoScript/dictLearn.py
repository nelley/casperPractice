#-*- coding:utf-8 -*-
import os
import sys
import jieba
import jieba.posseg
import codecs
import types
import json
import re
import time


re_han_default = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&\._%]+)", re.U)
types.GeneratorType

sys.path.insert(0, '/home/nelley/casperPractice/PTT/mongoScript')
from trie import *

jieba.set_dictionary('/home/nelley/casperPractice/PTT/mongoScript/dict.txt')
#stop = stopwords.words('/home/nelley/casperPractice/PTT/mongoScript/stopwords.txt')
jieba.enable_parallel(4)

str_list = ['小明畢業於日本早稻田大學院,之後到忠孝東路走九遍', '今天是2015年9月3号，去天安门广场庆祝抗战胜利70周年', '台灣的大哥角頭們為非作歹，一旦曝光，就逃往中國大陸，儼然成為黑道避難所。但中國國家主席習近平，日前下令全國掃黑，第一刀就砍向滯留的台灣黑道。粗估被通緝的有600多人，一半以上都想辦法要回台灣，因為大陸的苦牢實在不人道，20幾人擠在小舍房。 如今大哥逃難潮，也讓台灣警方始料未及，希望能將他們逮捕歸案。']

def word_seg(L):
    #print('original=%s' % L)

    #只有精確模式(cut_all=False)有修改成返回type
    outputObj = jieba.cut(L, cut_all=False, HMM=True)
    #outputObj = jieba.cut_for_search(L)

    result = ''
    for x in outputObj:
        #print(x)
        result += x[0] + '(' + x[1] + ')' + '/'
    print(result)

    return outputObj
    

def fun_test(sen):
    temp = jieba.posseg.cut(sen, HMM=True)
    #temp = jieba.cut_for_search(sen)
    output = ('/'.join(t.flag) for t in temp)
    for t in temp:
        print('word=%s, flag=%s' % (t.word, t.flag))
    print(output)
    #print ('/'.join(temp))

'''for unit test'''
def str_list_test():

    for tmp_str in str_list:
        blocks = re_han_default.split(tmp_str)
        for blk in blocks:
            add(root, blk)


if __name__ == '__main__':
    start_time = time.time()
    param = sys.argv
    dir_name = param[1]

    root = TrieNode('*')

    for filename in os.listdir(dir_name):
        if filename.endswith('txt'):
            print('filename=%s start process' % filename)
            content = codecs.open(dir_name + filename, 'r', 'utf-8').read()
            blocks = re_han_default.split(content)
            for blk in blocks:
                add(root, blk)
        print('filename=%s END process' % filename)

    
    serialize_all(json.dumps(root))
    print('Processed Time:%0.2f seconds' % (time.time() - start_time))
    restored_root = deserialize_all()
    get_all_in_depth(restored_root)

    print('---------------------------------------------')
    print(find_prefix(root, '，'))


