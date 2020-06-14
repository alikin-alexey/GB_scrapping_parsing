# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 02:13:28 2020

@author: USER
"""

import requests
from bs4 import BeautifulSoup as bs
import re
from pprint import pprint
from pymongo import MongoClient, errors


client = MongoClient('localhost',27017)
db = client['vacancies']
hh = db.hh

link = 'https://hh.ru'
text = 'инженер электрик'
area_num = 2

def page_data(soup):
    #блок со всеми вакансиями листа
    vac_block = soup.find('div', {'class':'vacancy-serp'})
    #список вакансий
    vac_list = vac_block.find_all('div', {'class':'vacancy-serp-item'}, recurcive=False)
    #данные по каждой вакансии
    for vac in vac_list:
        vac_dict = {}
        vac_dict['name'] = vac.find('a', {'data-qa':'vacancy-serp__vacancy-title'}).text            
        vac_dict['salary'] = vac.find('div', {'class':'vacancy-serp-item__sidebar'}).text
        if '-' in vac_dict['salary']:
            res = re.search(r'([\d ]+\D*[\d ]*)-([\d ]+\D*[\d ]*)',vac_dict['salary'])
            vac_dict['min_salary'] = int(''.join(res.group(1).split()))
            vac_dict['max_salary'] = int(''.join(res.group(2).split()))
        elif 'от' in vac_dict['salary']:
            res = re.search(r'([\d]+\D*[\d]*) ',vac_dict['salary'])
            vac_dict['min_salary'] = int(''.join(res.group(1).split()))
            vac_dict['max_salary'] = ''
            
        elif 'до' in vac_dict['salary']:
            res = re.search(r'([\d]+\D*[\d]*) ',vac_dict['salary'])
            vac_dict['max_salary'] = int(''.join(res.group(1).split()))
            vac_dict['min_salary'] = ''
            
        else:
            None
        if vac_dict['salary']:
            vac_dict['currency'] = re.search(r' ([\w\.]+$)',vac_dict['salary']).group(1)
        else:
            None
        vac_dict['link'] = vac.find('a', {'data-qa':'vacancy-serp__vacancy-title'})['href']
        if vac.find('a', {'data-qa':'vacancy-serp__vacancy-employer'}):
            vac_dict['company'] = vac.find('a', {'data-qa':'vacancy-serp__vacancy-employer'}).text
        else:
            vac_dict['company']='not_found'
        vac_dict['city'] = vac.find('span', {'data-qa':'vacancy-serp__vacancy-address'}).text
        vac_dict['source'] = 'hh.ru'
        vac_dict['date'] = vac.find('span', {'class':'vacancy-serp-item__publication-date'}).text
        #проверка наличия вакансии в базе
        vac_dict['_id'] = '~'.join([vac_dict['company'],vac_dict['name'],vac_dict['salary'],vac_dict['date']])
        try:
            hh.insert_one(vac_dict, {'$set':vac_dict})
        except errors.DuplicateKeyError:
            print(f"попытка вставить дублирующуюся вакансию: {vac_dict['_id']}")
        


def scrap_hh(link, text, area_num):
    area = area_num
    vacancy_name = text
    url = link
    params = {'area':area,
              'st':'searchVacancy',
              'text': vacancy_name,
              'fromSearch':'true'}
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    rq = requests.get(url+'/search/vacancy', params=params, headers=headers)
    soup = bs(rq.text, 'lxml')
    page_data(soup)

    print(f'страница {1} добавлена')
    pager_block = soup.find('div', {'data-qa':'pager-block'})
    next_page_tail = pager_block.find('a', {'data-qa':'pager-next'})
    i  = 2 
    
    while next_page_tail:
        soup = bs(requests.get(url+next_page_tail['href'], headers = headers).text, 'lxml')
        page_data(soup)
        pager_block = soup.find('div', {'data-qa':'pager-block'})
        next_page_tail = pager_block.find('a', {'data-qa':'pager-next'})
        print(f'страница {i} добавлена')
        i = i + 1

    


def filter(salary):
    for vac in hh.find({'$or':[{'min_salary':{'$gt':salary}},{'max_salary':{'$gt':salary}}]}, {'id':1}):
        pprint(vac)


scrap_hh(link, text, area_num)

