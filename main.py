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

#送信データ削減のためにサンプリングする（100個のデータを送信する）
def sample_temp(records):
	temp_list = []
	date_list = set({})
	# サンプル数は100
	sample_times = (records).count() / 100
	# もしサンプル回数が1以下の場合はすべて抽出する
	if( sample_times < 1 ):
		sample_times = 1
	ii = 0
	for record in records:
		ii = ii + 1
		# 日付は重複がないように集合とする
		date_list = date_list | set(record['date'].strftime("%Y_%m_%d"))
		# サンプル間隔以上の場合に送信データを追加する
		if ii >= sample_times :
			ii = 0
			temp_list.append({'date':record['date'].strftime("%Y,%m,%d,%H,%M,%S"), 'temp':record['temp1'], 'temp2':record['temp2'], 'humidity':record['humidity']})
	return temp_list, date_list

#すべての情報を取得する
@app.route('/')
def index():
	records=collection.find()
	temp_list, date_list = sample_temp(records)
	return render_template('index.html', temp_list=temp_list, date_list=date_list)

#h時間前からの情報を取得する
@app.route('/hour/<int:h>')
def hour(h):
	query = { "date" : { "$gte" : datetime.datetime.now() - datetime.timedelta(hours=h) } };
	records=collection.find(query)
	temp_list, date_list = sample_temp(records)
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
	
	temp_list, date_list = sample_temp(records)
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
	
