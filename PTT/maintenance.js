print('hello');
conn = new Mongo("192.168.8.129:27017");
db = conn.getDB('admin');
db.auth("root","notsniw0405");

db = conn.getDB('PTT');
cnt=0;

db.URL_list.find({'category':'salary', 'modified_date':{$ne:""}}).forEach(function(doc){
    //print(doc.post_time);
    if(typeof(doc.modified_date) != 'object'){
        print(doc.modified_date);
        //cnt++;
        /*
        tmp = doc.post_time.replace(" ","T").replace(/\//g,"-");
        db.Posts.update(
            {_id: doc._id},
            {"$set": {"post_time":ISODate(tmp + ".000Z")}}
        );*/
    }
    //print(typeof(doc.post_time));
    
    /*
    tmp = doc.modified_date.replace(" ","T").replace(/\//g,"-");
    print(ISODate(tmp + ".000Z"));
    
    db.URL_list.update(
        {_id: doc._id},
        {"$set": {"modified_date":ISODate(tmp + ".000Z")}}
    );*/
});

//print(cnt);
