# -*- coding:utf-8 -*-
"""
@author:zyl
@file:Weibo.py
@time:2018/12/30 22:57
"""
import requests
import time
from urllib  import parse
from pyquery import PyQuery as pyq
import weiboinfo
import random
def spider(user_id,num):
	url="https://m.weibo.cn/api/container/getIndex?"
	params={
		"type":"uid",
		"value":user_id,
		"containerid":"107603"+str(user_id),
		"page":num
	}
	url=url+parse.urlencode(params)
	headers={
		'user-agent': 'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)'
		              'AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'}
	r =requests.get(url,headers=headers)
	if r.status_code == 200: #判断是否正常连接
		return r.json()
	else:
		print("访问超时... 请检查网络连接")
		return None
def all(num):   # 对长文章的爬取即实现了阅读全文的功能
	url="https://m.weibo.cn/statuses/extend?id="+str(num)
	headers = {
		'referer':'https://m.weibo.cn/status/'+str(num),
		'user-agent': 'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)'
		              'AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
	'X-Requested-With':'XMLHttpRequest'}
	r = requests.get(url, headers=headers)
	if r.status_code == 200 :
		return r.json()
	else:
		print("访问超时... 请检查网络连接")
		return None


def parse_json(jso):
	if jso is not None:  #判断是否获取到信息
		items=jso.get('data').get('cards')
		for item in items:
			a=item.get('mblog')
			if a is None: # 判断是否为空文章 因为空文章无法使用get方法
				continue
			elif a['isLongText'] : # 判断是否为长文章
				p=all(a['id'])
				if p.get('data') is None:
					continue
				else:
					b={'text':pyq(p.get('data')['longTextContent']).text(),'date':a['created_at']}#pyq()调用pyquery去除html符号
					with open('text.txt','a',encoding='utf-8') as f:
						f.write(str(b))
						f.write('\n')
					#print(b)
			elif not a['isLongText']:
				b = {'text': pyq(a['text']).text(), 'date': a['created_at']}
				with open('text.txt','a',encoding='utf-8') as f:
					f.write(str(b))
					f.write('\n')
				#print(b)
	else:
		print("用户不存在或已注销...")

def main():
	#user_ids=[]
	for user_id in weiboinfo.user_ids:   #遍历用户id数组
	#user_id=2830678474                  # 需要自己输入用户的uid
		for i in range(1,11):            #这是设定爬取第一页到第十页
			json=spider(user_id,i)       #i表示为正在爬取微博的当前页数 最多为前100页
			parse_json(json)
			time.sleep(random.uniform(0.8, 1.2))                #放止访问的过于频繁
if __name__ == '__main__':
	main()
