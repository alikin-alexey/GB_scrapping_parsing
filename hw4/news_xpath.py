# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 22:45:50 2020

@author: USER
"""

import requests
from lxml import html
import re
from pymongo import MongoClient
from datetime import date
import time



client = MongoClient('localhost',27017)
db = client['news']
mail_ru = db.mail_ru
lenta_ru = db.lenta_ru
yandex_news = db.yandex_news

def news_mail_ru():
    url = 'https://news.mail.ru'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    response = requests.get(url + '/economics/', headers = headers)
    root = html.fromstring(response.text)
    #курс валют
    exchange_rates = root.xpath("//div[@class='p-rate-inf']/table//tr/td")
    for rate in exchange_rates:
        for x in rate.xpath(".//span[@class ='p-informer__params']/text()"):
            mail_ru.insert_one({'kind':'exchange rate',
                                'currency':re.search('([\w ]+)[\n\t]*([\w ]+)',x).group(1),
                                'source':re.search('([\w ]+)[\n\t]*([\w ]+)',x).group(2),
                                'date': str(date.today())})
    
    #главные 4 новости
    for x in root.xpath("//div[@class='block']//div[@class='grid__fixer']"):
        published = date.today()
        print(published)
        news_name = x.xpath(".//span[@class='photo__title']//text()")[0]
        print(news_name)
        deeplink = url+x.xpath('.//@href')[0]
        print(deeplink)
        time.sleep(5)
        resp = requests.get(deeplink, headers = headers)
        rt = html.fromstring(resp.text)
        source = rt.xpath("//div[@class='block']//span[@class='breadcrumbs__item']//a//text()")[0]
        print(source)
        mail_ru.insert_one({'kind':'news',
                            'date':str(published),
                            'news_name':news_name,
                            'link':deeplink,
                            'source':source})
    

    
    
def news_lenta_ru():
    url = 'https://lenta.ru'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    response = requests.get(url + '/rubrics/economics/', headers = headers)
    root = html.fromstring(response.text)
    #главная новость
    header = root.xpath("//div[@class='b-feature__header']//text()")
    link = root.xpath("//section[@class='b-feature js-feature b-feature_article']//a[@class='js-dh picture']//@href")
    published = root.xpath("//div[@class='g-date']//text()")
    source = 'lenta.ru'
    lenta_ru.insert_one({'kind':'main news',
                         'date': published,
                         'source':source,
                         'link': url+link[0],
                         'header': header})
    #псоледние новости
    items = root.xpath("//section[@class='b-yellow-box js-yellow-box']//div[@class='item']")
    for item in items:
        tail = item.xpath('.//a//@href')
        published = item.xpath(".//time//@datetime")[0]
        header = item.xpath(".//a/text()")[0]
        source = 'lenta.ru'
        if 'https' in tail[0]: 
            link = tail[0]
        else: 
            link = url+tail[0]
        lenta_ru.insert_one({'kind':'last news',
                             'date':published,
                             'header':header,
                             'source':source,
                             'link':link})

    
    
    
  

def news_yandex_news():
    url = 'https://news.yandex.ru/news/rubric/business?from=index'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    response = requests.get(url + '/rubrics/economics/', headers = headers)
    root = html.fromstring(response.text)
    main_block = root.xpath("//div[@class='stories-set__main-item']")
    tail = main_block[0].xpath(".//div[@class='story__content']//h2[@class='story__title']//@href")[0]
    link = 'https://news.yandex.ru' + tail
    header = main_block[0].xpath(".//div[@class='story__content']//h2[@class='story__title']//text()")[0]
    source = main_block[0].xpath(".//div[@class='story__content']//div[@class='story__info']//text()")[0]
    published = date.today()
    yandex_news.insert_one({'kind':'main_news',
                            'header':header,
                            'link':link,
                            'source':source,
                            'date':str(published)})
    
 
    

    
    
news_mail_ru()
news_lenta_ru()
news_yandex_news()
