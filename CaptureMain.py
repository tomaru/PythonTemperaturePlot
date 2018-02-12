# -*- coding: utf-8 -*-
"""
データをプロットする
"""

import os,sys
import time
import datetime

from library import HttpRequestData

from pymongo import MongoClient

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.Header import Header

#=====================================================#

def save_db(collection, temp1, temp2, humidity, date=None):
	data = {}
	if date == None:
		data['date'] =  datetime.datetime.now()
	else:
		data['date'] =  date
	print("date %s" % data['date'])
	data['temp1'] = temp1
	data['temp2'] = temp2
	data['humidity'] = humidity
	
	collection.insert(data)

#=====================================================#


FROM_ADDRESS = 'sender@gmail.com'
MY_PASSWORD = 'password'
def create_message(from_addr, to_addr, bcc_addrs, ubject, body):
	msg = MIMEMultipart()
	msg['From'] = from_addr
	msg['To'] = to_addr
	msg['Bcc'] = bcc_addrs
	msg['Date'] = formatdate()
	msg['Subject'] = (subject)
	body = MIMEText(body)
	msg.attach(body)
	return msg

def send(from_addr, to_addrs, msg):
	try:
		smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
		##smtpobj.connect("smtp.gmail.com",587)
		smtpobj.ehlo()
		smtpobj.starttls()
		smtpobj.ehlo()
		smtpobj.login(FROM_ADDRESS, MY_PASSWORD)
		smtpobj.sendmail(from_addr, to_addrs, msg.as_string())
		print( 'Send Mail Success' )
	except Exception as e:
		print('SendMail Failed')
		print(e)
	finally:
		smtpobj.close()
	
	
#=====================================================#

if __name__ == "__main__":
	### Create Data Base
	client = MongoClient('localhost', 27017)
	db = client['test-database']
	collection = db["Index"]
	### Captured Thread
	# Get Object
	getdata = HttpRequestData.HttpRequestData()
	##
	#first_time = datetime.datetime.now()
	tstr = '2012-12-29 13:49:37'
	first_time = datetime.datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')
	while 1:
		# 気温と湿度を取得する
		temp1,temp2,humidity = getdata.get_temperature("http://192.168.2.100/")
		time.sleep(3)
		if temp2!=-999:
			# データベースへ保存する
			#print("temp1 %s" % temp1)
			#print("temp2 %s" % temp2)
			#print("humidity %s" % humidity)
			save_db(collection, temp1, temp2, humidity)
		else:
			last_time =  datetime.datetime.now()
			delta = last_time - first_time
			print(delta.total_seconds())
			if( 10*60 <= delta.total_seconds() ):
				first_time =  datetime.datetime.now()
				to_addr = 'rcver@gmail.comm'
				BCC = ''
				subject = 'エラー:TemperatureServer'
				body = '室温の取得に失敗しました'
				msg = create_message(FROM_ADDRESS, to_addr, BCC, subject, body)
				send(FROM_ADDRESS, to_addr, msg)
			
			