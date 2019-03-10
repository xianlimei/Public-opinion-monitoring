# -*- coding:utf-8 -*-
"""
@author:zyl
@file:people.py
@time:2018/12/3 18:34
"""
import requests
from bs4 import BeautifulSoup
import re
import savefile
import time
import bs4 #再次导入bs包是为了解释器能识别出bs4
import random
def spider(url):
	headers={
		'user-agent': 'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)'
		              'AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'}
	r =requests.get(url,headers=headers)
	r.encoding="gbk"         # 否则会乱码，要根据页面所确定
	if r.status_code == 200: #判断是否正常连接
		return r.text
	else:
		return None
def parse_list(html):
	soup = BeautifulSoup(html, "lxml")
	div1=soup.find('div',class_="w1000")
	print("正在获取板块列表...")
	for item in div1:
  	'''
		判断是否是bs4的tag对象 且其子节点存在 a标签 此处需import bs4  
		因为 不仅存在 Tag <a> 还存在 NavigableString 换行 
		Beautiful Soup用 NavigableString 类来包装tag中的字符串
		'''
		if isinstance(item,bs4.element.Tag) and item.a is not None:  
			href=item.a['href']
			parse_html(href)
			time.sleep(1.5)
def parse_html(href):
	html=spider(href)
	path=savefile.auto_parse_file("E:\ProGraming\Code\public media",'people')
	soup = BeautifulSoup(html, "lxml")
	a=soup.find_all('a')
	pattern = re.compile('/n1.*?')
	for item in a:
		if item.get('href',None) is not None:  #判断 a 标签是否存在 href 对象 或属性
			if pattern.match(item.get('href')):
				href='http://politics.people.com.cn/'+item.get('href')
				news_list=[]                       #列表初始化 每访问一个新版块就初始化 防止list元素过多 降低查找效率
				parse_news(href,path,news_list)
				print("正在爬取新闻列表...")
				time.sleep(random.uniform(0.8, 1.2))
def parse_news(href,path,news_list):
	if href not in news_list:                 #判断该链接是否曾访问过
		html=spider(href)
		news=BeautifulSoup(html,"lxml")
		day = time.strftime('%d', time.localtime(time.time()))
		title=news.find('title').string.replace('\xa0'," ")
		keywords = news.find("meta", attrs={'name': "keywords"})['content']  # 获取关键词
		times = news.find("meta", attrs={'name': "publishdate"})['content']
		article=""
		div=news.find('div',class_="box_con")
		if div is not None:                    #判断是否存在目标div
			p=div.find_all('p')
			for item in p:
				if item.string is not None:        #判断该标签下是否有文章/字符串
        '''
        去除乱码，据爬取页面情况而定
        '''
					article = article + item.string.replace('\n','').replace('\t','').replace('\u3000','').replace('\xa0'," ").replace('■'," ") 
				else:
					print("内容为空,停止写入...")
			news_article = {'title': title, 'time': times, 'keywords': keywords, 'article': article}
			print("正在写入...请稍后")
			with open(path+'\\' + day + '.txt', 'a',encoding="utf+8") as f:
				f.write(str(news_article))
				f.write('\n')
				news_list.append(href)             #将访问过的链接存起来,用于去重
				print("写入成功")
		else:
			print("div不存在,停止写入...")
	else:
		print("该新闻已存在,停止写入...")
def main():
	print("正在启动爬虫程序...")
	start=time.time()
	html=spider(url='http://www.people.com.cn/')
	parse_list(html)
	end=time.time()
	use_time=(end-start)/60
	print("任务完成")
	print("本次用时"+use_time+"分")
if __name__ == '__main__':
	main()
