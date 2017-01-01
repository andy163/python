#!/usr/bin/python
#-*- coding: utf-8 -*-


import os,sys
import MySQLdb
import ConfigParser
 
# import HiveLogger          #写日志
# y=HiveLogger.HiveLogger(__file__)  #获取日志对象

class lib_mysql_query(object):
	
	def __init__(self):
			
		global db
		global cursor
                reload(sys)
                #sys.setdefaultencoding('utf-8')
                cf = ConfigParser.ConfigParser() 
                cf.read("config.ini")
                db_ip = cf.get("baseinfo", "db_ip")
                db_user = cf.get("baseinfo", "db_user")
                db_pwd = cf.get("baseinfo", "db_pwd")
                db_name = cf.get("baseinfo", "db_name")
                #db = MySQLdb.connect(host = '192.168.1.2', user='root',passwd = 'invenodb123',db = 'db_mta')
		db = MySQLdb.connect(host = db_ip, user=db_user,passwd = db_pwd,db = db_name)
		cursor = db.cursor()
                db.set_character_set('utf8')
                cursor.execute('SET NAMES utf8;') 
                cursor.execute('SET CHARACTER SET utf8;')
                cursor.execute('SET character_set_connection=utf8;')

	def mysql_query(self,sql):
		try:
			result = cursor.execute(sql)
                        db.commit()
			return result
		except MySQLdb.Error, e:
			print e
			return 2
		
	def mysql_insert(self,sql):
		try:
			cursor.execute(sql)
                        db.commit()
			return 1
		except MySQLdb.Error, e:
			print e
			return 2
		
	def mysql_query_count(self,sql):
		try:
			cursor.execute(sql)
			results = cursor.fetchall();
			return results[0][0];
		except MySQLdb.Error, e:
			print e
			return 0
				
	def __del__(self):
			cursor.close()
			db.close()
