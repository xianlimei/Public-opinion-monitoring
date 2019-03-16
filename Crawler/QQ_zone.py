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
class QQ_Spider(object):
    def __init__(self,user,password):
        '''
        初始化
        '''
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path='E:\Office worke\chormedrive\chromedriver.exe',options=self.chrome_options)# 需安装chormediver 注意版本对应 若是firefox 则应下载对应驱动
        self.driver.get('https://i.qq.com/')
        self.__username = user#输入你的QQ号
        self.__password = password #输入你的密码
        self.headers = {
            'host': 'h5.qzone.qq.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'connection': 'keep-alive'
        }
        self.req = requests.Session()  #保持会话
        self.cookies = {}
    def get_qq_num(self):  
    '''
    确定要爬取的目标好友
    '''
        qq_num=[]
        print('输入你要爬取的目标好友qq，可以输入多个，以回车隔开，以0结束')
        while(1):
            qq=input()
            if qq is not '0':
                qq_num.append(qq)
            else:
                break
        self.qq_num=qq_num
    def login(self):
        '''
        登录、调用get_g_tk()、get_friends()函数
        :return:
        '''
        self.driver.switch_to.frame('login_frame')
        self.driver.find_element_by_id('switcher_plogin').click()
        self.driver.find_element_by_id('u').clear()
        self.driver.find_element_by_id('u').send_keys(self.__username)
        self.driver.find_element_by_id('p').clear()
        self.driver.find_element_by_id('p').send_keys(self.__password)
        self.driver.find_element_by_id('login_button').click()
        time.sleep(1) #等待浏览器加载
        self.driver.get('http://user.qzone.qq.com/{}'.format(self.__username))
        #cookie = ''
        cookie={}
        for item in self.driver.get_cookies():
            cookie[item["name"]]=item['value']  #拼接cookie为字典

        self.cookies = cookie
        self.get_g_tk()
        #self.headers['Cookie'] = self.cookies
        self.driver.quit()


    def get_g_tk(self):
        '''
        获取g_tk()
        '''
        p_skey=self.cookies['p_skey']
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        self.g_tk = h & 2147483647

    def get_info(self):
        '''
        构造说说请求链接
        正则解析
        '''
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
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        for q in self.qq_num:
            t1, pos = True, 0
            url_ = url + '&uin=' + str(q)
            while(t1):
                url__ = url_ + '&pos=' + str(pos)
                info = self.req.get(url=url__, headers=self.headers,cookies=self.cookies)
                if '\"msglist\":null' in info.text or "\"message\":\"对不起,主人设置了保密,您没有权限查看\"" in info.text:
                    t1 = False
                    if '\"message\":\"对不起,主人设置了保密,您没有权限查看\"' in info.text:
                        print("对不起,主人设置了保密,您没有权限查看")

                else:
                    created_time = re.findall('created_time":\d+', info.text)
                    contents = re.findall('],"content":".*?"', info.text)
                    comment_content = re.findall('commentlist":(null|.*?],)', info.text)
                    comments = re.findall('cmtnum":\d+', info.text)
                    remove_emotion=re.compile('\[em\].*?]')  #匹配qq内置表情
                    for _time,  _content, _comment_content, _comment in \
                            zip(created_time,  contents, comment_content, comments):
                        _comment_content=re.sub(remove_emotion,'',_comment_content) #表情过滤
                        _content = re.sub(remove_emotion, '', _content)
                        data = {
                            'QQ':str(q),
                            'CreateTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(re.sub('created_time":', '', _time)))),
                            'content': re.sub('],"content":"|"', '', _content),
                            'comment_content': re.sub('null|commentlist":', '', _comment_content) if 'null' in _comment_content else str([(re.sub('content":"|"', '', x), re.sub('createTime2":"|"', '', y), re.sub('name":"|"', '', z), re.sub('uin":', '', zz)) for x, y, z, zz in zip(re.findall('content":".*?"', _comment_content), re.findall('createTime2":".*?"', _comment_content), re.findall('name":".*?"', _comment_content), re.findall('uin":\d+', _comment_content))]),
                            'comment': re.sub('cmtnum":', '', _comment),
                        }
                        with open('QQinfo.txt', 'a', encoding='utf-8') as f:
                            f.write(str(data) + "\n")
                            f.close()
                            print("写入成功")
                    pos += 20
                    time.sleep(random.uniform(4.5, 5.5))
if __name__ == '__main__':
    user=input('输入账号')
    password=input('输入密码')
    qq_crawler = QQ_Spider(user,password)
    qq_crawler.get_qq_num()
    qq_crawler.login()
    qq_crawler.get_info()
