# -*- coding: utf-8 -*-
"""
データをプロットする
"""

import os,sys
import datetime

from pymongo import MongoClient

from flask import Flask, render_template, request

app = Flask(__name__)

#=====================================================#

#すべての情報を取得する
@app.route('/')
def index():
	records=collection.find()
	temp_list = []
	date_list = set({})
	for record in records:
		date_list = date_list | set({record['date'].strftime("%Y-%m-%d")});
		temp_list.append({'date':record['date'].strftime("%Y,%m,%d,%H,%M,%S"), 'temp':record['temp1'], 'temp2':record['temp2'], 'humidity':record['humidity']})
	return render_template('index.html', temp_list=temp_list, date_list=date_list)

#h時間前からの情報を取得する
@app.route('/hour/<int:h>')
def hour(h):
	query = { "date" : { "$gte" : datetime.datetime.now() - datetime.timedelta(hours=h) } };
	
	records=collection.find(query)
	temp_list = []
	date_list = set({})
	for record in records:
		date_list = date_list | set(record['date'].strftime("%Y-%m-%d"));
		temp_list.append({'date':record['date'].strftime("%Y,%m,%d,%H,%M,%S"), 'temp':record['temp1'], 'temp2':record['temp2'], 'humidity':record['humidity']})
	return render_template('index.html', temp_list=temp_list, date_list=date_list)


@app.route('/post', methods=['GET', 'POST'])
def post():
	if request.method == 'POST' :
		date_start = request.form['date_start']
		date_end = request.form['date_end']
		if date_start != "" and date_end != "":
			query = { "date" : { "$gte" : datetime.datetime.strptime(date_start, '%Y-%m-%d') ,"$lte": datetime.datetime.strptime(date_end, '%Y-%m-%d') } };
			records=collection.find(query)
		else:
			records=collection.find()
	else:
		records=collection.find()

	temp_list = []
	date_list = set({})
	for record in records:
		date_list = date_list | set(record['date'].strftime("%Y_%m_%d"));
		temp_list.append({'date':record['date'].strftime("%Y,%m,%d,%H,%M,%S"), 'temp':record['temp1'], 'temp2':record['temp2'], 'humidity':record['humidity']})
	return render_template('index.html', temp_list=temp_list, date_list=date_list)

#=====================================================#

if __name__ == "__main__":
	### Create Data Base
	client = MongoClient('localhost', 27017)
	db = client['test-database']
	collection = db["Index"]

	### APP
	app.debug = True
	#app.run(host="0.0.0.0")
	app.run()
	
