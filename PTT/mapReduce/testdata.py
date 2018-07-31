


from bson.code import Code
from pymongo import MongoClient

def get_db():
    client = MongoClient('192.168.8.129:27017')
    db = client.helloworld
    db.authenticate("root", "notsniw0405", source="admin")
    return db




if __name__ == '__main__':
    conn = get_db()
    result = conn.things.insert_many([{"x": 1, "tags": ["dog", "cat"]},
                                    {"x": 2, "tags": ["cat"]},
                                    {"x": 2, "tags": ["mouse", "cat", "dog"]},
                                    {"x": 3, "tags": []}])
    
