# -*- coding: utf-8 -*-

import os.path as op
import os
import requests
from selenium import webdriver
import json
import time
import datetime
import datetime
import vk_api
from Tkinter import *
from tkFileDialog import *
import threading
from xml.dom.minidom import *
from mutagen.mp3 import MP3
from mutagen import id3 as mu
import urllib as ul
import httplib as hl
import random
import string

try:
	from pync import Notifier
except:
	print "error Notifier"
#import pynotify



settings_file="set.py"
ARTWORK_TAG = u'APIC:'
MIME_PNG = 'image/png'
MIME_JPEG = 'image/jpeg'
FRONT_COVER = 3
SIZE_34X34=b'small'
SIZE_64X64=b'medium'
SIZE_174X174=b'large'
SIZE_300X300=b'extralarge'
SIZE_RAW=b'mega'
driver = webdriver.Firefox()
app_title = "vkCheck"

driver.get("https://oauth.vk.com/authorize?client_id=3682744&v=5.7&scope=wall,audio,offline&redirect_uri=http://oauth.vk.com/blank.html&display=page&response_type=token")



# user_input = driver.find_element_by_name("email")
# user_input.send_keys(user)
# password_input = driver.find_element_by_name("pass")
# password_input.send_keys(password)
submit = driver.find_element_by_id("install_allow")

# submit.click()

current = driver.current_url
access_list = (current.split("#"))[1].split("&")
access_token = (access_list[0].split("="))[1]
expires_in = (access_list[1].split("="))[1]
user_id = (access_list[2].split("="))[1] 

driver.close()

def massage(msg):
	try:
		Notifier.notify(msg, title="VKCheck")
	except:
		print msg
	


massage("Подключение установлено")

url = "https://api.vkontakte.ru/method/" \
     "audio.get?uid=" + user_id +\
     "&access_token=" + access_token#+\
      #"&captcha_sid=899026847011&captcha_key=sydy"

def LfmLikeRequest(word):
	z=[(' ',"+"), (".", "+"),("++", "+")]
	for p in z: 
		word=word.replace(p[0],p[1])
	return word

def fBindArtwork(sTrackAddr, sImgAddr, sArtAppend=u'frontcover'):

    muTrack=MP3(sTrackAddr)
    fPicture=file(sImgAddr, 'rb')
    sPic=fPicture.read()
 
    if op.splitext(sImgAddr)[-1].lower()=='png': sMimeType=MIME_PNG
    elif (op.splitext(sImgAddr)[-1].lower()=='jpg'
        or op.splitext(sImgAddr)[-1].lower()=='jpeg'
        or op.splitext(sImgAddr)[-1].lower()=='jpe'): sMimeType=MIME_JPEG
    else: sMimeType=''
 
    sArtworkTag=ARTWORK_TAG+sArtAppend

    muPic=mu.APIC(encoding=3, mime=MIME_JPEG, type=FRONT_COVER,
        desc=u'Album front cover', data=0)

    muTrack.tags[sArtworkTag]=muPic

    muTrack.tags[sArtworkTag].data=sPic
    muTrack.save(v1=2)
 	
    fPicture.close()

def fDownload(sSource):
	
    fSourceImg = ul.urlopen(sSource)
    sTarget = "downloads/img/"
    now_time = datetime.datetime.now()
    name = now_time.strftime("%d%m%Y%I%M%S")
    ras = sSource[-4:]
    fTargetImg = open(sTarget+name+ras, "wb")
    sData = fSourceImg.read()
    fTargetImg.write(sData)
    fTargetImg.close()
    fSourceImg.close()
    return sTarget+name+ras


def check_tracks():
	massage("Проверка листа")
	artists_list = []
	titles_list = []
	links_list = []
	number = 0
	page = requests.get(url)
	html = page.text

	my_dict = json.loads(html) 
	for i in my_dict['response']:
	    artists_list.append(i['artist'])
	    titles_list.append(i['title'])
	    links_list.append(i['url'])
	    number += 1

	path = "downloads"

	if not os.path.exists(path):
	    os.makedirs(path)

	for i in range(0, number):
		new_filename = path+"/"+artists_list[i] + " - " + titles_list[i] + ".mp3"
		track_name = artists_list[i] + " - " + titles_list[i]
		if not os.path.exists(new_filename):
			massage(track_name)
			with open(new_filename, "wb") as out:
				response = requests.get(links_list[i].split("?")[0])
				out.write(response.content)
			art = LfmLikeRequest(artists_list[i])
			song = LfmLikeRequest(titles_list[i])
			try:
				last = 'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=a407aee358200d2368b5ee53141b6d77&artist='+art+'&track='+song+'&format=json'
				
				page = requests.get(last)
				html = page.text

				my_last = json.loads(html) 
				track = my_last['track']
				album = track['album']
				image = album['image']
				big_img = image[3]
				img_url = big_img['#text']

				pic_link = img_url
			except:
				
				last = 'http://ws.audioscrobbler.com/2.0/?method=artist.getInfo&api_key=a407aee358200d2368b5ee53141b6d77&artist='+art+'&format=json'
				except_page = requests.get(last)
				except_html = except_page.text

				except_my_last = json.loads(except_html) 
				track = except_my_last['artist']
				artist = track['image']
				big_img = artist[4]
				img_url = big_img['#text']
				pic_link = img_url
				if len(pic_link)==0:
					pic_link = "http://image1.pricedekho.com/p/5/51217/142306-apple-ipod-mc297hna-160gb-picture-large.jpg"
			#print "Link: " + pic_link 	
			path_to_pic = fDownload(pic_link)
			time.sleep(5)
			fBindArtwork(new_filename, path_to_pic, sArtAppend=u'frontcover')
while True:

	check_tracks()
	time.sleep(60)