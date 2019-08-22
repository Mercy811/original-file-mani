'''
	ALREADY KNOW: total number of chineseX is 10657

	TYPES of english url:
		<a href=\"http://www.infoq.com/news/2007/04/google-soc-ruby-summary\">您可以通过此链接查看英文原文</a>
		<p><strong>查看英文原文</strong>：<a href=\"http://www.infoq.com/articles/0-bugs-policy\">0 Bugs Policy</a>

'''

# encoding=utf8

import json
import re
import decimal
import os

from simplejson import OrderedDict
import simplejson 

from topic import topicDic

path = os.environ['HOME']+"/Documents/"

class TopicError(Exception):
	'''
		if one article do not get a topic then raise this error 
	'''
	def __init__(self, args):
		self.args = args

def prettyJson(content):
	''' convert format with SublimePrettyJson

		arg:
			String content
		
		return:
			String neatContent
	'''

	# load 
	obj = simplejson.loads(content,
							  object_pairs_hook=OrderedDict,
							  parse_float=decimal.Decimal)

	# dump

	s = {
		"use_entire_file_if_no_selection": True,
		"indent": 2,
		"sort_keys": False,
		"ensure_ascii": False,
		"line_separator": ",",
		"value_separator": ": ",
		"keep_arrays_single_line": False,
		"max_arrays_line_length": 120,
		"pretty_on_save": False,
		"validate_on_save": True
	}

	sort_keys = True

	line_separator = s.get("line_separator", ",")
	value_separator = s.get("value_separator", ": ")

	output_json = simplejson.dumps(obj,
							 indent=s.get("indent", 2),
							 ensure_ascii=s.get("ensure_ascii", False),
							 sort_keys=sort_keys,
							 separators=(line_separator, value_separator),
							 use_decimal=True)

	# do we need try and shuffle things around ?
	post_process = s.get("keep_arrays_single_line", False)

	if post_process:
		# find all array matches
		matches = re.findall(r"\[([^\[\]]+?)\]", output_json)
		join_separator = line_separator.ljust(2)
		for m in matches:
			items = [a.strip() for a in m.split(line_separator.strip())]
			replacement = join_separator.join(items)
			# if line not gets too long, replace with single line
			if len(replacement) <= s.get("max_arrays_line_length", 120):
				output_json = output_json.replace(m, replacement)

	return output_json

def cleanChinese():
	'''
		clean text from hbase get content,title
		write URL (from Folder-chineseUrl), CONTENT and TITLE to Folder-chineseOriginalFile 
	'''
	for i in range(1,10658):
		with open(path+'chinese/chinese'+str(i),'r') as f:
			data1 = f.read()
	
		dataDict = json.loads(prettyJson(data1)) 
		content = dataDict["data"]["content"]
		title = dataDict["data"]["article_title"]

		# use regular expression to clean content (remove html tags) AND get original link
		content = re.sub(r'<.{0,8}>|&#xD|;',"",content)
		

		# link inside an html tag
		match = re.search(u'\u67e5\u770b\u82f1\u6587\u539f\u6587(\u003a)*(\uff1a)*(\n)*(.*?)(\u200b)*( )*(\u00a0)*<a (.*?)href="(.*?)"',content)
		writeGroup = 9
		# link outside an html tag
		if match == None: # 查看英文原文 : ：
			match = re.search(u'\u67e5\u770b\u82f1\u6587\u539f\u6587(\u003a)*(\uff1a)*(\n)*(.*?)(\u200b)*( )*(\u00a0)*(.*?)\n',content)
			writeGroup = 8
		if match == None: #<a href=\"http://www.infoq.com/news/2007/04/google-soc-ruby-summary\">您可以通过此链接查看英文原文</a>
			match = re.search(u'href=\\"(.*?)\\">\u60a8\u53ef\u4ee5\u901a\u8fc7\u6b64\u94fe\u63a5\u67e5\u770b\u82f1\u6587\u539f\u6587',content)
			writeGroup = 1

		# remove remained html tags [this step has to be after extract englishUrl]
		content = re.sub(r'<.*?>',"",content)

		with open(os.environ['HOME']+'/documents/chineseUrl/chinese'+str(i)) as f:
			url = f.read()

		finalContent = "URL "+url+"\nTITLE "+title+"\nCONTENT\n\n"+content

		# 写文件
		with open(path+'chineseOriginalFile/chinese'+str(i),'w') as f:
			f.write(finalContent)
		
		try:
			with open(path+'originalLink/chinese'+str(i),'w') as f:
				f.write(match.group(writeGroup))
		except AttributeError:
			print("AttributeError: "+str(i))

def getTopic(fileName):
	'''
		arg:
			String fileName (eg: chinese1)(file from hbase)

		return:
			String topic
	'''
	with open(path+'chinese/'+fileName, 'r') as f:
		data1 = f.read()
	dataDict = json.loads(prettyJson(data1))
	topics = dataDict['data']['topic']
	
	for t in topics:
		if topicDic[t['name']] != '':
			topic = topicDic[t['name']]
			break
	if topic == '':
		raise TopicError('TopicError')
	else:
		#print(str(i)+"  |"+topic+" : "+topicDic[topic])
		return topic

def getTitle(fileName):
	'''
		arg: 
			String fileName (eg: chinese1)(file from englishOriginalFile)

		return:
			String title
	'''
	
	# find line number of CONTENT
	lookup = 'CONTENT'
	title = ''
	with open(path+'test/'+fileName,'r') as myFile:
		data1 = myFile.readlines()
		for num, line in enumerate(data1, 1):
			if lookup in line:
				#print('found CONTENT at line: '+str(num))
				line_CONTENT = num
				break
		for i in data1[2:line_CONTENT-1]:
			title += re.sub(r'\t|\n|/|','',i)
	
	return title

def setFileName(fileName):
	'''
		TYPE: Article            |Book, Article, Whitepaper, Subscript
		CATEGORY: getTopic()     |Tech, Tool, Platform, Language&Framework, Method
		SOURCE: Infoq            |TW, Infoq, Other
		TITLE: getTitle()
		LANGUAGE:                |zh, en
	'''
	try:
		category = getTopic(fileName)
		title = getTitle(fileName)
		englishName = 'Article_'+category+'_Infoq_'+title+'_en'
		chineseName = 'Article_'+category+'_Infoq_'+title+'_zh'
		os.rename(path+'chineseOriginalFile/'+fileName, path+'chineseOriginalFile/'+chineseName)
		os.rename(path+'englishOriginalFile/'+fileName, path+'englishOriginalFile/'+englishName)
	except TopicError:
		print("================ TopicError: "+fileName +" ====================")
	except FileNotFoundError:
		print("================ FileNotFoundError: "+fileName +" ====================")
		print(chineseName)
	else:
		print("successfully set file name: "+fileName)

def formatFileName(fileName):
	'''
		remove tokens in file name
		add .txt extension 
	'''
	formatedName = re.sub("\'|’",'',fileName)
	formatedName = re.sub('“|"|\?|,|\$|\(|\)|\.\.\.|\+|&','',formatedName)
	formatedName = re.sub('/|\.|#|:|;','-',formatedName)
	formatedName = re.sub('@|<|>',' ',formatedName)
	formatedName = formatedName+'.txt'
	os.rename(path+'/articles/'+fileName, path+'/articles/'+formatedName)

	return formatedName

if __name__ == '__main__':

	files = os.listdir(path+'articles')
	for f in files:
		if re.search('en.txt',f) != None:
			print(f)
			lookup = 'CONTENT'
			title = ''
			with open(path+'articles/'+f,'r+') as myFile:
				data1 = myFile.readlines()
				for num, line in enumerate(data1, 1):
					if lookup in line:
						line_CONTENT = num
						break
				for i in data1[2:line_CONTENT-2]:
					title += re.sub(r'\t|\n|/|','',i)
				data1[1] = 'TITLE '+title
				for i in range(2,line_CONTENT-2):
					data1.pop(i)
				myFile.seek(0)
				myFile.truncate()
				for item in data1:
					myFile.write(item)


	### set file name
	##	ChineseOriginalFile/chineseX -> TYPE_CATEGORY_SOURCE_TITLE_LANGUAGE
	##	englishOrigianlFile/chineseX -> TYPE_CATEGORY_SOURCE_TITLE_LANGUAGE
	##	manually, put both chinese and english article in one Folder-original_files/articles
	##
	##	do not 
	##		1. remove tokens
	##		2. add .txt extension 
	##	use formatFileName to do this
	###
	# files = os.listdir(path+'englishOriginalFile')
	# for f in files:
	# 	if re.search('chinese', f) != None:
	# 		setFileName(f)



	### delete chinese files
	## 	after set file name using code above, chinese articles and english articles are in
	##	two different Folders- chineseOriginalFile and englishOrigianlFile
	##	manually, move these two articles into one Folder-origianl_files/articles
	## 	files with name chineseX are all chinese articles without english articles
	## 	run the code behind to delete there files
	# files = os.listdir(path+'database/original_files/articles')
	# for f in files:
	# 	if re.match('chinese',f) != None:
	# 		os.remove(path+'database/original_files/articles/'+f)
	# 		print("successfully delete file: "+f)


	### format file name 
	# files = os.listdir(path+'articles')
	
	# for f in files:
	# 	if f != '.DS_Store':
	# 		print("format file: "+formatFileName(f))
			


