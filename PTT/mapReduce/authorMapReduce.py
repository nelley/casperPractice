from bson.code import Code
from pymongo import MongoClient

def get_db():
    client = MongoClient('192.168.8.129:27017')
    db = client.PTT
    db.authenticate("root", "notsniw0405", source="admin")
    return db



if __name__ == '__main__':
    print 'start'
    conn = get_db()
    
    map = Code(open('authorMap.js','r').read())
    reduce = Code(open('authorReduce.js', 'r').read()) 

    results = conn.Posts.map_reduce(map, reduce, "myresults")

    for result in results:
        print result



    print 'end'


