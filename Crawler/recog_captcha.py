# -*- coding:utf-8 -*-
"""
@author:zyl
@file:recog_captcha.py
@time:2019/3/31 13:06
"""
import requests
from PIL import Image
import re
from selenium import webdriver
import sys
import time
from selenium.webdriver import ActionChains
import random
def recog_Verification_code(driver):
	# driver=webdriver.Chrome(executable_path='E:\Office worke\chormedrive\chromedriver.exe')
	# driver.get("https://ssl.zc.qq.com/v3/index-chs.html?type=3")
	driver.switch_to.frame('tcaptcha_iframe')  #进入到验证码frame
	time.sleep(0.5)
	print("发现验证码...")
	print("启动验证码识别模块...")
	real_size,image_url=get_Verification_image(driver)
	image1=Image.open('image1.png')
	image2 = Image.open('image2.png')
	print("正在验证...")
	width, height = image1.size
	left=get_gap(image1,image2)
	# print(left)
	# print(width)
	# print(real_size)
	left=left*(real_size['width']/width)-32.8
	# print(left)
	track=get_track(left)
	slice=driver.find_element_by_id('tcaptcha_drag_thumb')
	count=0
	while 1:
		boolen,url=isElementExist(driver,'slideBg')
		if boolen and url==image_url:
			move_to_gap(driver, slice, track)
			count+=1
		elif boolen and url!=image_url:
			real_size,image_url = get_Verification_image(driver)
			image1 = Image.open('image1.png')
			image2 = Image.open('image2.png')
			width, height = image1.size  #获取所下载图片的宽和高
			left = get_gap(image1, image2)
			# print(width)
			# print(real_size)
			left = left * (real_size['width']/ width) - 32.8 #由于所获取图像大小与实际有偏差故要进行等比例转换，32.8是滑块的起始位置与边界的差值
			# print(left)
			track = get_track(left)
			slice = driver.find_element_by_id('tcaptcha_drag_thumb')
			move_to_gap(driver, slice, track)
			count += 1
		elif count >= 18 :
			print("验证失败,请升级验证模块...")
			sys.exit(1)
		else:
			break
	print('验证成功...')

def isElementExist(driver,element_id):  #判断验证码是否存在，用于检测是否验证通过
	try:
		image=driver.find_element_by_id(element_id)
		image_url=image.get_attribute('src')
		return True,image_url
	except:
		return False,None


def get_Verification_image(driver):
	# js = "document.getElementById('slideBg').removeAttribute('unselectable')"
	# driver.execute_script(js)
	bg=driver.find_element_by_id('slideBg')
	image_url=bg.get_attribute('src')
	r=requests.get(url=image_url)  #获取有缺块图像
	with open('image1.png','wb',) as f:
		f.write(r.content)
		f.close()
	image_url=re.sub('_1_','_0_',image_url)
	r=requests.get(url=image_url)  #获取原图
	with open('image2.png','wb',) as f:
		f.write(r.content)
		f.close()
	image_url = re.sub('_0_', '_1_', image_url)
	return bg.size,image_url

def is_pixel_equal(image1,image2,x,y):  #判断像素点是否相同
	pixel1=image1.load()[x,y]
	pixel2 = image2.load()[x, y]
	threshold = 60   #设定阈值
	if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
			pixel1[2] - pixel2[2]) < threshold:
		return True
	else:
		return False

def get_gap( image1, image2):
	"""
	获取缺口偏移量
	:param image1: 带缺口图片
	:param image2: 不带缺口图片
	:return:
	"""
	left = 340  #从中间开始判断，一般在右边，减少判断次数，提高效率
	for i in range(left, image1.size[0]):
		for j in range(image1.size[1]):
			if not is_pixel_equal(image1, image2, i, j):
				left = i
				return left
	return left


def get_track( distance):
	"""
	根据偏移量获取移动轨迹
	:param distance: 偏移量
	:return: 移动轨迹
	"""
	# 移动轨迹
	track = []
	# 当前位移
	current = 0
	# 减速阈值
	mid = distance * random.uniform(0.73,0.91) #随机生成，保证下次通过率
	# 初速度
	v = 0

	while current < distance:
		t = random.uniform(0.10, 0.18) 	# 计算间隔，每次计算一步更新一次
		if current < mid:
			a = random.uniform(1.3,1.8)  #随机加速度
		else:
			a = random.uniform(-2.0,-1.4)
		# 初速度v0
		v0 = v
		# 当前速度v = v0 + at
		v = v0 + a * t
		# 移动距离x = v0t + 1/2 * a * t^2
		move = v0 * t + 1 / 2 * a * t * t
		# 当前位移
		current += move
		# 加入轨迹
		track.append(round(move))
	return track

def move_to_gap(browser,slider, track):
	"""
	拖动滑块到缺口处
	:param slider: 滑块
	:param track: 轨迹
	:return:
	"""
	ActionChains(browser).click_and_hold(slider).perform()
	for x in track:
		ActionChains(browser).move_by_offset(xoffset=x, yoffset=0).perform() #控制并移动滑块
	time.sleep(random.uniform(0.57,0.67)) #稳定滑块
	ActionChains(browser).release().perform() #释放滑块
	time.sleep(random.uniform(0.26,0.34)) #若未验证正确，等待滑块归位
# if __name__ == '__main__':
# 	recog_Verification_code()
