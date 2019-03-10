# -*- coding:utf-8 -*-
"""
@author:zyl
@file:savefile.py
@time:2019/3/2 11:01
"""
import os
import time
'''
  自定义储存文件函数 四个参数分别是：
  path-初始路径，之后程序后再当前路径下创建文件夹
  media-媒体名称 year-年 month-月
'''
def customize_parse_file(path,media,year,month):  
	if os.path.exists(path):
		if os.path.exists(path+'\\'+media):
			if os.path.exists(path+'\\'+media+'\\'+year):
				if os.path.exists(path+'\\'+media+'\\'+year+'\\'+month):
					path=path+'\\'+media+'\\'+year+'\\'+month
					return path
				else:
					os.makedirs(path +'\\'+ media + '\\' +year+'\\'+ month )
					path = path + '\\' + media + '\\' + year + '\\' + month
					return path
			else:
				os.makedirs(path +'\\'+ media + '\\' +year+'\\'+ month )
				path = path + '\\' + media + '\\' + year + '\\' + month
				return path
		else:
			os.makedirs(path +'\\'+ media + '\\'+year+'\\' + month )
			path = path + '\\' + media + '\\' + year + '\\' + month
			return path
	else:
		os.makedirs(path+'\\' + media + '\\'+year+'\\' + month )
		path = path + '\\' + media + '\\' + year + '\\' + month
		return path
'''
  自动储存文件函数 两个参数分别是：
  path-初始路径，之后程序后再当前路径下创建文件夹
  media-媒体名称 时间会自动设定为当前年月
'''
def auto_parse_file(path,media):         
	year = time.strftime('%Y', time.localtime(time.time()))
	month =time.strftime('%m', time.localtime(time.time()))
	if os.path.exists(path):
		if os.path.exists(path+'\\'+media):
			if os.path.exists(path+'\\'+media+'\\'+year):
				if os.path.exists(path+'\\'+media+'\\'+year+'\\'+month):
					path = path + '\\' + media + '\\' + year + '\\' + month
					return path
				else:
					os.makedirs(path +'\\'+ media + '\\' +year+'\\'+ month )
					path = path + '\\' + media + '\\' + year + '\\' + month
					return path
			else:
				os.makedirs(path +'\\'+ media + '\\' +year+'\\'+ month )
				path = path + '\\' + media + '\\' + year + '\\' + month
				return path
		else:
			os.makedirs(path +'\\'+ media + '\\'+year+'\\' + month )
			path = path + '\\' + media + '\\' + year + '\\' + month
			return path
	else:
		os.makedirs(path +'\\'+ media + '\\'+year+'\\' + month )
		path = path + '\\' + media + '\\' + year + '\\' + month
		return path
