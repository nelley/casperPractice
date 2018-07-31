# -*- coding: utf-8 -*-
import sys
import os
import json

def get_db():
    from pymongo import MongoClient
    client = MongoClient('192.168.8.129:27017')
    db = client.PTT
    db.authenticate("root", "notsniw0405", source="admin")
    return db

def add_post(db, collection):
    db[collection].insert({"category" : "gossip", "text":"test"})
    
def get_post_find_one(db, collection):
    return db[collection].find_one()

def get_post_all(db,collection):
    return db[collection].find()

def remove_documents(db, collection):
    return db[collection].delete_many({})

