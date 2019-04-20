# -*- coding:utf-8 -*-
"""
@author:zyl
@file:qq_crawler.py
@time:2019/3/16 10:28
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import random
import requests
from urllib import parse
import multiprocessing
from multiprocessing import Pool,freeze_support
import json
import os
import sys
import recog_captcha
from requests.adapters import HTTPAdapter
import datetime
class QQ_Spider(object):
	def __init__(self,user,password):
		'''
		初始化
		'''
		print("系统正在初始化...")
		self.chrome_options = Options()
		self.chrome_options.add_argument('--headless')
		self.driver_zone = webdriver.Chrome(executable_path='E:\Office worke\chormedrive\chromedriver.exe',options=self.chrome_options)# 需安装chormediver 注意版本对应 若是firefox 则应下载对应驱动
		self.driver_zone.get('https://i.qq.com/')
		self.driver_mail = webdriver.Chrome(executable_path="E:\Office worke\chormedrive\chromedriver.exe",options=self.chrome_options)
		self.driver_mail.get('https://mail.qq.com/')
		self.__username = user#输入你的QQ号
		self.__password = password #输入你的密码
		print("系统初始化完成...")
	def QQ_zone_login(self):
		'''
		登录、调用get_g_tk()函数
		:return:
		'''
		print("系统运行中...")
		self.driver_zone.switch_to.frame('login_frame')
		self.element = self.driver_zone.find_element_by_id('switcher_plogin')
		if self.element.is_displayed():
			self.driver_zone.find_element_by_id('switcher_plogin').click()
		self.driver_zone.find_element_by_id('u').clear()
		self.driver_zone.find_element_by_id('u').send_keys(self.__username)
		self.driver_zone.find_element_by_id('p').clear()
		self.driver_zone.find_element_by_id('p').send_keys(self.__password)
		self.driver_zone.find_element_by_id('login_button').click()
		goal_url='https://user.qzone.qq.com/{}'.format(self.__username)
		time.sleep(0.8)
		self.cookie_zone = {}
		cookie_zone = {}
		count=0
		while 1:
			if self.driver_zone.current_url !=goal_url and count<=3:
				time.sleep(1) #等待浏览器加载
				count=count+1
			elif self.driver_zone.current_url != goal_url and count>3 :
				recog_captcha.recog_Verification_code(self.driver_zone)  #进行验证码识别
				break
			else:
				break
		self.driver_zone.get('https://user.qzone.qq.com/{}'.format(self.__username))
		#cookie = ''
		for item in self.driver_zone.get_cookies():
			#cookie += item["name"] + '=' + item['value'] + ';'  #拼接cookie 为字符串
			cookie_zone[item["name"]]=item['value']  #拼接cookie为字典
		if not ('p_skey' in cookie_zone.keys()):
			print("获取cookie值失败，请稍后再试...")
			sys.exit(1)
		self.cookie_zone = cookie_zone
		# print(cookie_zone)
		#self.headers['Cookie'] = self.cookies
		self.driver_zone.quit()
		return cookie_zone

	def QQ_mail_login(self):
		self.driver_mail.switch_to.frame('login_frame')  # 登录在该frame内
		self.element=self.driver_mail.find_element_by_id('switcher_plogin')
		if self.element.is_displayed():  #判断该切换按钮是否存在
			self.driver_mail.find_element_by_id('switcher_plogin').click()
		self.driver_mail.find_element_by_id('u').clear()
		self.driver_mail.find_element_by_id('u').send_keys(self.__username)
		self.driver_mail.find_element_by_id('p').clear()
		self.driver_mail.find_element_by_id('p').send_keys(self.__password)
		self.driver_mail.find_element_by_id('login_button').click()
		time.sleep(0.8)
		goal_url='https://mail.qq.com/cgi-bin/readtemplate?check=false&t=loginpage_new_jump&vt=passport&vm=wpt&ft=loginpage&target=&account={}'.format(
				self.__username)
		count=0
		while 1:
			if self.driver_mail.current_url !=goal_url and count<=3:
				time.sleep(1) #等待浏览器加载
				count=count+1
			elif self.driver_mail.current_url == goal_url and count>3 :
				recog_captcha.recog_Verification_code(self.driver_mail)  #进行验证码识别
				break
			else:
				break
		self.driver_mail.get(
			'https://mail.qq.com/cgi-bin/readtemplate?check=false&t=loginpage_new_jump&vt=passport&vm=wpt&ft=loginpage&target=&account={}'.format(
				self.__username))
		# cookie={}
		cookie_mail = ''
		for item in self.driver_mail.get_cookies():
			cookie_mail += item["name"] + '=' + item['value'] + ';'  # 拼接cookie 为字符串
		# cookie[item["name"]] = item['value']
		self.cookie_mail=cookie_mail
		self.driver_mail.quit()
		# print(cookie)
	def get_qq_num(self,qq_num):
		print("加载指定QQ获取模块...")
		print("加载完成...")
		print('输入你要爬取的目标好友qq，可以输入多个，以回车隔开，以0结束')
		while(1):
			qq=input()
			if qq is not '0':
				qq_num.put(qq)
			else:
				break
	def get_QQgroup(self,qq_num):
		print("加载分组获取模块...")
		url = "https://mail.qq.com/cgi-bin/login?vt=passport&vm=wpt&ft=loginpage&target="
		headers = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'zh-CN,zh;q=0.9',
			'referer': 'https://mail.qq.com/',
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
			, 'cookie': self.cookie_mail
		}
		session = requests.Session()
		# session.mount('http://', HTTPAdapter(max_retries=3))
		# session.mount('https://', HTTPAdapter(max_retries=3)) #设置超时重试次数
		res = session.post(url=url, headers=headers, allow_redirects=False)
		location = res.headers['location']
		sid = location[location.find('sid=') + 4:location.find('&', location.find('sid='))]
		url2 = 'https://mail.qq.com/cgi-bin/laddr_lastlist?' + 'sid=' + sid + '&encode_type=js&t=addr_datanew&s=AutoComplete&category=hot&resp_charset=UTF8&ef=js&r=0.010669463067699336'  # r的值为18位随机数,可以写死
		header = {
			'accept': '*/*',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'zh-CN,zh;q=0.9',
			'cookie': self.cookie_mail,
			'referer': 'https://mail.qq.com/zh_CN/htmledition/ajax_proxy.html?mail.qq.com&v=140521',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
		}
		requ = requests.get(url=url2, headers=header)
		text=requ.text[1:len(requ.text) - 1]  # 去除源数据中的圆括号
		qq_groups = text[text.find('qqgroups : ') + 11:text.find(',groups :', text.find('qqgroups : '))]  # 截取qqgroups那一块数据
		# print(qq_groups)
		sortbyupdatetime = requ.text[requ.text.find('sortbyupdatetime : ') + 19:requ.text.find(',qqgroups :',requ.text.find('sortbyupdatetime : '))]  # 截取sortbyupdatetime那一块数据,为进行qq号转换
		# print(sortbyupdatetime)
		qq_groups = re.sub(re.compile('."\0"'), '', qq_groups)  # 除去空字符，防止eval函数报错 该函数不能处理空字符
		qq_groups = eval(qq_groups)  # 将字符串转为list
		sortbyupdatetime = re.sub(re.compile('."\0"'), '', sortbyupdatetime)  # 除去空字符，防止eval函数报错 该函数不能处理空字符
		sortbyupdatetime = re.sub(re.compile('@qq.com'), '', sortbyupdatetime)
		# print(sortbyupdatetime)
		sortbyupdatetime = eval(sortbyupdatetime)  # 将字符串转为list
		# print(type(sortbyupdatetime))
		for i,item in zip(range(len(qq_groups)),qq_groups) :
			print(str(int(i)) + ' : ' + item[2])  # 显示分组信息 并打印
		# for item in sortbyupdatetime:
		# 	# print(item[0])
		# 	if int(len(item[0])) < 10 or  re.findall('[a-zA-Z] ',item[0]):
		# 		sortbyupdatetime.remove(item)
		# 		print('ok')
		in_list = []
		count=0
		for group in qq_groups:
			count=count+len(group[1])
		count = len(sortbyupdatetime)-count
		# print(count)
		for group in qq_groups:  #进行qq号转换
			for num, i in zip(range(0, len(group[1])), range(count, count + len(group[1]))):
				if str(group[1][num]) == sortbyupdatetime[i][0]:
					group[1][num] = sortbyupdatetime[i][2]
			# print(group[0])
					# print(group[1][num])
					# print(sortbyupdatetime[i][2])
			count = count + len(group[1])
		print("加载完成...")
		print('请选择你要爬取的分组(输入对应分组的索引,可输入多个，以-1结束):')
		while (1):          #分组信息输入入口
			i = int(input())
			if i is not -1:
				in_list.append(i)
			else:
				break
		for i in in_list:    #将所选分组qq号填充到队列中
			for num in qq_groups[i][1]:
				qq_num.put(num)
				# print(num)
		#print(self.qq_num)
	def mode_choose(self,qq_num):
		print("请选择爬取模式：1：指定QQ 2：指定分组 3：混合模式 ")
		mode = int(input())
		if mode is 1:
			self.get_qq_num(qq_num)
		elif mode is 2:
			self.get_QQgroup(qq_num)
		else:
			self.get_qq_num(qq_num)
			self.get_QQgroup(qq_num)
	def get_g_tk(self):
		'''
		获取g_tk()
		'''
		p_skey=self.cookie_zone['p_skey']
		h = 5381
		for i in p_skey:
			h += (h << 5) + ord(i)
		self.g_tk = h & 2147483647
		return self.g_tk
	def set_time(self):
		time_list=[7,30,90,180,365]
		print("请选择所要爬取的时间段：")
		for i in range(5):
			if i==0:
				print(str(i)+" : "+"近一周")
			if i==1:
				print(str(i)+" : "+"近一月")
			if i==2:
				print(str(i)+" : "+"近三月")
			if i==3:
				print(str(i)+" : "+"近半年")
			if i==4:
				print(str(i)+" : "+"近一年")
		number=int(input())
		#now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.time_set = (datetime.datetime.now()-datetime.timedelta(days=time_list[number])).strftime("%Y-%m-%d %H:%M:%S")#获取时间界限，number是几天
		#print(time_set)
		return self.time_set
def get_info(g_tk,cookie_zone,qq_num,time_set):
	'''
	构造说说请求链接
	正则解析
	'''
	req = requests.Session()  # 保持会话
	url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
	params = {
		'inCharset': 'utf-8',
		'outCharset': 'utf-8',
		'sort': 0,
		'num': 20,
		'repllyunm': 100,
		'cgi_host': 'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',
		'callback': '_preloadCallback',
		'code_version': 1,
		'format': 'jsonp',
		'need_private_comment': 1,
		'g_tk': g_tk
	}
	headers = {
		'host': 'h5.qzone.qq.com',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'zh-CN,zh;q=0.8',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
		'connection': 'keep-alive'
	}
	url = url + parse.urlencode(params)
	while 1:
		if not qq_num.empty():
			q=qq_num.get()
			t1, pos = True, 0
			url_ = url + '&uin=' + str(q)
			while(t1):
				url__ = url_ + '&pos=' + str(pos)
				info = req.get(url=url__, headers=headers,cookies=cookie_zone)
				r = re.findall('\((.*)\)', info.text)[0]
				inf = json.loads(r)
				if '\"msglist\":null' in info.text or "\"message\":\"对不起,主人设置了保密,您没有权限查看\"" in info.text:
					t1 = False
					if '\"message\":\"对不起,主人设置了保密,您没有权限查看\"' in info.text:
						print("对不起,主人设置了保密,您没有权限查看")
				else :
					if 'msglist' in inf:
						msglist = inf['msglist']
						if msglist:
							for m in msglist:
								uid_name = m['name']
					created_time = re.findall('created_time":\d+', info.text)
					contents = re.findall('],"content":".*?"', info.text)
					comment_content = re.findall('commentlist":(null|.*?],)', info.text)
					comments = re.findall('cmtnum":\d+', info.text)
					remove_emotion=re.compile('\[em\].*?]')
					for _time,  _content, _comment_content, _comment in \
							zip(created_time,  contents, comment_content, comments):
						_comment_content=re.sub(remove_emotion,'',_comment_content)
						_content = re.sub(remove_emotion, '', _content)
						current_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(re.sub('created_time":', '', _time))))
						if current_time<time_set:
							break
						data = {
							'nickname':uid_name,
							'QQ':str(q),
							'CreateTime': current_time,
							'content': re.sub('],"content":"|"', '', _content),
							'comment': re.sub('cmtnum":', '', _comment),
							'comment_content': re.sub('null|commentlist":', '', _comment_content) if 'null' in _comment_content else str([(re.sub('content":"|"', '', x), re.sub('createTime2":"|"', '', y), re.sub('name":"|"', '', z), re.sub('uin":', '', zz)) for x, y, z, zz in zip(re.findall('content":".*?"', _comment_content), re.findall('createTime2":".*?"', _comment_content), re.findall('name":".*?"', _comment_content), re.findall('uin":\d+', _comment_content))]),
						}
						with open('QQinfo.txt', 'a', encoding='utf-8') as f:  #存储说说信息
							f.write(str(data) + "\n")
							f.close()
							#pid = os.getpid()  # 得到当前进程号
							# print('当前进程号：%s   ' % pid)
							print("写入成功...")
					if current_time < time_set:
						break
					pos += 20
					time.sleep(random.uniform(4.0, 5.0))
		else:
			return 'Queue is empty'

if __name__ == '__main__':
	freeze_support()
	manager = multiprocessing.Manager()
	qq_num = manager.Queue()  # 初始化要爬取的qq列表,必须用multiprocess的manager下的queue 才能保持通信
	user=input('请输入账号: ')
	password=input('请输入密码: ')
	process=int(input("请输入要开启的进程数: "))  #设定开启进程
	qq_zone_crawler = QQ_Spider(user,password)
	time_set=qq_zone_crawler.set_time()
	cookie_zone=qq_zone_crawler.QQ_zone_login()
	g_tk=qq_zone_crawler.get_g_tk()
	qq_zone_crawler.QQ_mail_login()
	qq_zone_crawler.mode_choose(qq_num)
	a = time.time()
	p=Pool(process)
	results=[]
	for i in range(process):
		try:
			results.append(p.apply_async(get_info, args=(g_tk,cookie_zone,qq_num,time_set)))
		except  Exception as e:
			print(e)
	p.close()
	p.join()
	for res in results:
		print(res.get())  #查看运行结果
	b=time.time()
	print("总用时：%0.5f"%(b-a))
