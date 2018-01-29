# -*- coding: utf-8 -*-
"""
データをプロットする
"""

import os,sys
import time
import datetime

from library import HttpRequestData

from pymongo import MongoClient

#=====================================================#

def save_db(collection, temp1, temp2, humidity, date=None):
	data = {}
	if date == None:
		data['date'] =  datetime.datetime.now()
	else:
		data['date'] =  date
	data['temp1'] = temp1
	data['temp2'] = temp2
	data['humidity'] = humidity
	
	collection.insert(data)
	
#=====================================================#

if __name__ == "__main__":
	### Create Data Base
	client = MongoClient('localhost', 27017)
	db = client['test-database']
	collection = db["Index"]
	### Captured Thread
	# Get Object
	getdata = HttpRequestData.HttpRequestData()
	while 1:
		# 気温と湿度を取得する
		temp1,temp2,humidity = getdata.get_temperature("http://192.168.2.100/")
		time.sleep(3)
		if temp2!="-128":
			# データベースへ保存する
			#print("temp1 %s" % temp1)
			#print("temp2 %s" % temp2)
			#print("humidity %s" % humidity)
			save_db(collection, temp1, temp2, humidity)