from bson.code import Code
from pymongo import MongoClient

def get_db():
    client = MongoClient('192.168.8.129:27017')
    db = client.PTT
    db.authenticate("root", "notsniw0405", source="admin")
    return db



mapper = Code("""
               function () {
                 this.tags.forEach(function(z) {
                   emit(z, 1);
                 });
               }
               """)

mapper = Code("""
                function(){
                    emit(this.author,{count:1});

                }
             """)

#key:emit function's arg1
#values:emit funtion's arg2
reducer = Code("""
                function (key, values) {
                  var total = 0;
                  for (var i = 0; i < values.length; i++) {
                    total += values[i];
                  }
                  return total;
                }
                """)

reducer = Code("""
                function (key, values) {
                    var total = 0;
                    values.forEach(function(value){
                        total += value.count;
                    })
                    return total;
                }
                """)

if __name__ == '__main__':
    conn = get_db()
    '''
    result = conn.things.map_reduce(mapper, reducer, "myresults")
    for doc in result.find():
        print doc
    '''
    result = conn.Posts.map_reduce(mapper, reducer, "myresults")
    for doc in result.find():
        print doc
 

    #result = conn.things.find()
    #for doc in result:
    #    print doc

