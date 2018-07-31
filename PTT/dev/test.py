# -*- coding: utf-8 -*-

import sys
import psycopg2

if __name__ == "__main__":
    param = sys.argv
    #print param[1]
    try:
        conn=psycopg2.connect("dbname='ptt' user='postgres' host='192.168.8.129' password='notsniw0405'")
    except:
        print "I am unable to connect to the database."

    cur = conn.cursor()

    try:
    	cur.execute("SELECT * FROM techjob")
        rows = cur.fetchall()
        print rows
    except Exception as e:
        print e
    


