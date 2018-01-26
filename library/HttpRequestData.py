#!/usr/bin/env python
# coding:utf-8

import os
import re
import sys
import datetime
import ConfigParser
import requests
from bs4 import BeautifulSoup

#=====================================================#

def print_debug_log(str):
#	if not __debug__:
	print(str)

#=====================================================#
def check_encoding(str):
	print chardet.detect(str)
		
#=====================================================#
def guess_charset(data):  
	f = lambda d, enc: d.decode(enc) and enc  
  
	try: return f(data, 'utf-8')  
	except: pass  
	try: return f(data, 'shift-jis')  
	except: pass  
	try: return f(data, 'ascii')  
	except: pass  
	try: return f(data, 'euc-jp')  
	except: pass  
	try: return f(data, 'iso2022-jp')  
	except: pass  
	return None  
  
#=====================================================#
def conv(data):  
	charset = guess_charset(data)  
	u = data.decode(charset)  
	return u.encode('utf-8')  
	
#=====================================================#
def read_config(tag, name):
	""" read config file and  return value."""
	config_path = './config/config.ini'
	try:
		ini_reader = ConfigParser.SafeConfigParser()
		ini_reader.read(config_path)
		return ini_reader.get(tag, name)
	except ConfigParser.NoSectionError:
		exit("[Exit] ERROR: ConfigParser.NoSectionError, tag: %s, name: %s"
			% (tag, name))
	except ConfigParser.NoOptionError:
		exit("[Exit] ERROR: ConfigParser.NoOptionError, tag: %s, name: %s"
			% (tag, name))

#=====================================================#
# HttpRequestDataクラス
#=====================================================#

class HttpRequestData(object):
	""" Crawlするクラス"""

	DEFAULT_TIMEOUT = int(read_config("Access", "timeout"))
	MAX_ACCESS_COUNT = int(read_config("Access", "max_access_count"))

#=====================================================#

# log 出力関数
	@staticmethod
	def log(depth, tag_name, msg):
		if depth == 0: print "\n"
		print "\t" * depth +  "[%s] %s" % (tag_name ,msg)

#=====================================================#

# html or csv の出力関数
	@staticmethod
	def _file_write(file_name, data, file_type="html", url=None, params=None):
		log_name = "Write to File"
		log_depth = 1

		separate_str = "\n--------------------\n"
		d = datetime.datetime.today()
		date_str = "%s-%s-%s_%s:%s:%s" % (d.year, d.month, d.day, d.hour, d.minute, d.second)

		if file_type == "html":
			dir_path = read_config("Log", "html_dir")
			# OSによって決まっているセパレータ記号に置換する
			dir_path = dir_path.replace('/',os.sep)
			name_extension = ".html"
		elif file_type == 'csv':
			dir_path = read_config("Log", "html_dir")
			# OSによって決まっているセパレータ記号に置換する
			dir_path = dir_path.replace('/',os.sep)
			name_extension = ".csv"
		else:
			dir_path = read_config("Log", "dir")
			# OSによって決まっているセパレータ記号に置換する
			dir_path = dir_path.replace('/',os.sep)
			name_extension = ".log"

		# ":"はWindows では使えないため置換する
		date_str = date_str.replace(":", "_");
		file_path = os.path.join(dir_path, file_name + "~" + date_str + name_extension)
		#HttpRequestData.log(log_depth,log_name, "try to write to file: %s" % (file_path))
		try:
			if file_type == 'html':
				f = open(file_path, 'w')
			else:
				f = open(file_path, 'wb')
			f.write(data)

			if not url is None: f.write(separate_str + "url: %s" %(url))
			if not params is None: f.write(separate_str + "request parameter: %s" %(params))

			f.close()
			HttpRequestData.log(log_depth,log_name, "SUCCESS: write to file: %s" % (file_path))
			return True, None
		except IOError:
			HttpRequestData.log(log_depth,log_name, "SUCCESS: write to file: %s" % (file_path))
			return False, "Occured IOError"
		except:
			HttpRequestData.log(log_depth,log_name, "SUCCESS: write to file: %s" % (file_path))
			return False, "Occured Something Error" 

#=====================================================#

	def __init__(self):
		""" initialize: set urllib2.opener """

#=====================================================#

# 引数のURLで情報を要求する
	def _open_url(self, url, params=None):
		""" try to access to `url` """
		decoded_html= ""
		
		log_depth = 1
		log_name = "Trying to Open Url"

		for i in range(self.MAX_ACCESS_COUNT):
			try:
				#self.log(log_depth, log_name, "access to %s (access count: %d)\n\t\t\tparams: %s" % (url, i+1, params))
				timeout = self.DEFAULT_TIMEOUT + i
				
				headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
				page = requests.get(url, timeout=timeout, params=params, headers=headers)
				
				
				if page.status_code == requests.codes.ok:
					# 取得成功
					self.log(log_depth, log_name, "SUCCESS: access to %s" % (url))
					
					#check_encoding(page.content)
					# HTMLをデコード
					if( page.content != "" ):
						content_type = page.headers["content-type"]
						if 'image' not in content_type:
							decoded_html = conv(page.content)
					#check_encoding(decoded_html)
				
					# ログとしてHTMLを書き込むかどうか判定
					#if int(read_config("Log", "enable")) == 1:
					#	self._file_write("PAGE", decoded_html,file_type="html", url=url, params=params)
						
					return decoded_html
				else:
					self.log(log_depth, log_name, "FAILURE: access to %s" % (url))
			except requests.exceptions.RequestException as e:  # This is the correct syntax
				self.log(log_depth, log_name, "FAILURE: access to %s" % (url))
		return decoded_html
		#sys.exit("[EXIT] cannot reach %s" % (url))

#=====================================================#
	
	def get_temperature(self, page_url):
		
		temperature = 0
		humidity = 0
		
		html = self._open_url(page_url)
		if( html != "" ):
			soup = BeautifulSoup(html, "html.parser")
			tds = soup.find_all('td')
			temperature = tds[0].text
			humidity = tds[1].text
		
		return temperature, humidity
#=====================================================#

if __name__ == "__main__":

	print_debug_log( "=== Callled : " + sys._getframe().f_code.co_name + " ===" )
	getdata = HttpRequestData.HttpRequestData()
	temp,humidity = getdata.get_temperature("http://192.168.2.100")
	print( temp )
	print( humidity )

# End of File #
