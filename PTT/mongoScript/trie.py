#-*- coding:utf-8 -*-
from typing import Tuple
import pdb
import jieba
import json
import types
types.GeneratorType

pdb.set_trace()

DUMP_PATH = '/home/nelley/casperPractice/PTT/mongoScript/'

class TrieNode(dict):
    """
    Our trie node implementation. Very basic. but does the job
    """
    #char=tuple:customized with return two values(char, type) from jieba
    def __init__(self, char: tuple, children=None, counter=None, word_finished=None, PredicType=None):
        super().__init__()
        #allow attribute access(by .)
        #without this, have to write as self['char'] = char
        self.__dict__ = self
        
        self.char = char

        #important!!Python uses that same persistent object that was created from the first call to the function
        #so it have to assign [] everytime
        if children is None:
            self.children = []
        else:
            self.children = children

        # Is it the last character of the word.
        if word_finished is None:
            self.word_finished = False
        else:
            self.word_finished = word_finished

        # How many times this character appeared in the addition process
        if counter is None:
            self.counter = 1
        else:
            self.counter = counter

        # PredicType after jieba process
        if PredicType is None:
            self.PredicType = 'unk'
        else:
            self.PredicType = PredicType

    @staticmethod
    def from_dict(_dict):
        """recursively reconstruct tree from dict"""
        root = TrieNode(_dict['char'], _dict['children'], _dict['counter'], _dict['word_finished'], _dict['PredicType'])
        """map(aFunction, a Iterable Sequence) return a list"""
        root.children = list(map(TrieNode.from_dict, root.children))
        return root

def add(root, sentence: str):
    """
    Adding a word in the trie structure
    """
    node = root
    
    if isinstance(sentence, types.GeneratorType):
        #under construction
        print('generator object')

    elif isinstance(sentence, str):
        word = jieba.cut(sentence, cut_all=False)
        for char in word:
            #print('ingest char=%s, type=%s' % (char[0], char[1]))
            found_in_child = False
            # Search for the character in the children of the present `node`
            for child in node.children:
                #print('child.char=%s, child=%s' % (child.char,char[0]))
                if child.char == char[0]:
                    # We found it, increase the counter by 1 to keep track that another
                    # word has it as well
                    child.counter += 1
                    # And point the node to the child that contains this char
                    node = child
                    found_in_child = True
                    break
            # We did not find it so add a new chlid
            if not found_in_child:
                new_node = TrieNode(char[0])    #initialize with string after jieba
                new_node.PredicType = char[1]   #assign type after jieba process
                node.children.append(new_node)
                # And then point node to the new child
                node = new_node
        # Everything finished. Mark it as the end of a word.
        node.word_finished = True

# -> annotated Tuple[bool, int] is the return value
def find_prefix(root, prefix: str) -> Tuple[bool, int]:
    """
    Check and return 
      1. If the prefix exsists in any of the words we added so far
      2. If yes then how may words actually have the prefix
      3. If yes then return the words in list
    """
    node = root

    hit_words = []
    word = ''
    # If the root node has no children, then return False.
    # Because it means we are trying to search in an empty trie
    if not root.children:
        return False, 0
    for char in prefix:
        char_not_found = True
        # Search through all the children of the present `node`
        for child in node.children:
            if child.char == char:
                word += child.char 
                # We found the char existing in the child.
                char_not_found = False
                # Assign node as the child containing the char and break
                node = child
                break
        # Return False anyway when we did not find a char.
        if char_not_found:
            return False, 0
    # Well, we are here means we have found the prefix. Return true to indicate that
    # And also the counter of the last node. This indicates how many words have this
    # prefix

    #print(word)
    return True, node.counter


"""
wrote by NELLEY 20180129
"""
def get_all_in_depth(root, char=''):
    node = root
    for child in node.children:
        result = char
        if child.children:
            #print('result=%s' % child.char[0])
            result += child.char + '(' + child.PredicType + ',' + str(child.counter) +')' +'/'
            get_all_in_depth(child, result)
    
        if child.word_finished:
            print('combined char=%s' % char + child.char + '(' + child.PredicType + ')')
           
def get_all_in_breadth(root):
    node = root
    queue_list = []
    for x in node.children:
        queue_list.append(x)

    while queue_list:
        obj = queue_list.pop(0)
        print('poped char=%s' % (obj.char))
        for x in obj.children:
            queue_list.append(x)
    return node

'''save trie result to file'''
def serialize_all(_dict):
    with open(DUMP_PATH + 'trieDump.txt', 'w') as outfile:
        jsonobj = json.dump(_dict, outfile)
    
'''read stored trie for processing'''
def deserialize_all():
    with open(DUMP_PATH + 'trieDump.txt', 'r') as infile:
        datarestore = json.loads(json.load(infile))
        #print(datarestore)
        return TrieNode.from_dict(datarestore)

def remove(root, word):

    node = root
    if not root.children:
        return False
    for char in word:
        char_not_found = True
        for child in node.children:
            if child.char == char:
                char_not_found = False
                node = child
                break

        if char_not_found:
            return False
    #print(node.char)


'''sort the json object'''
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def add_test(root):
    #add(root, 'hackathon is very interest lo')
    #add(root, 'hackathon is very hard')
    #add(root, 'hackathon is very shit')
    #add(root, 'hackathon is very good')
    #add(root, 'hackathon is' )
    #add(root, 'hackathon is like shit')
    #add(root, 'hackathon is like good')
    #add(root, 'hackathon wonderful')
    #add(root, 'hackathon is amazing')
    add(root, '台灣幅銳態')
    add(root, '幅銳態')
    add(root, '台灣塑膠')
    #add(root, '上海自來水來自海上')
    #add(root, '上海自來水來自台中')
    get_all_in_depth(root)
    return root

if __name__ == "__main__":
    root = TrieNode('*')
    
    #root = add_test(root)
    #print(find_prefix(root, ['上海','自來','水來','自台']))
    '''
    serialize_all(json.dumps(root))
 
    restored_root = deserialize_all()
    print('-------------------------')
    add(restored_root, '台灣大哥大')
    get_all_in_depth(restored_root)
    '''
    add_in_breadth(root)

    #print(ordered(root)==ordered(restored_root))
    #print(find_prefix(root, '台灣塑'))
    #print(find_prefix(root, 'hammer'))




