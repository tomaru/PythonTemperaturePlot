# -*- coding: utf-8 -*-
"""
データをプロットする
"""

import os,sys
import signal
import time
import threading

from library import HttpRequestData

from pymongo import MongoClient
from datetime import datetime

from flask import Flask, render_template

app = Flask(__name__)

#=====================================================#

@app.route('/')
def index():
	records=collection.find()
	print(records)
	temp_list = []
	for record in records:
		temp_list.append({'date':record['date'].strftime("%Y-%m-%d %H:%M"), 'temp':record['temp']})
	return render_template('index.html',title="TemperatureGraph", temp_list=temp_list)

#=====================================================#

def save_db( temp, date=None):
	
	data = {}
	if date == None:
		data['date'] =  datetime.now()
	else:
		data['date'] =  date
	data['temp'] = temp 
	
	collection.insert(data)
	
#=====================================================#

def print_debug_log(str):
#	if not __debug__:
	print(str)
	
def handler(signal, frame):
	print ("=======SYSTEM EXIT=======")
	stop_flag.set()

signal.signal(signal.SIGINT, handler)

class TestThread(threading.Thread):

	"""docstring for TestThread"""

	def __init__(self, t, stop_flag):
		super(TestThread, self).__init__()
		self.t = t
		self.stop_flag = stop_flag

	def run(self):
		# Get Object
		getdata = HttpRequestData.HttpRequestData()
		while 1:
			if self.stop_flag.is_set() :
				break
			# 気温と湿度を取得する
			temp,humidity = getdata.get_temperature("http://192.168.2.100/")
			time.sleep(self.t)
			if temp!=0:
				# データベースへ保存する
				save_db(temp=temp)

if __name__ == "__main__":
	### Create Data Base
	client = MongoClient('localhost', 27017)
	db = client['test-database']
	collection = db["Index"]
	### Captured Thread
	stop_flag = threading.Event() #停止させるかのフラグ
	th_cl = TestThread(1, stop_flag)
	th_cl.start()
	### APP
	app.debug = True
	app.run()
	
