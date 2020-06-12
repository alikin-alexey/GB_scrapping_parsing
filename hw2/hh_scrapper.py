# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:07:57 2020

@author: USER
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

link = 'https://hh.ru'
text = 'инженер электрик'
area_num = 2

def page_data(soup):
    #dataframe
    vacancies = pd.DataFrame()
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
            vac_dict['min_salary'] = res.group(1)
            vac_dict['max_salary'] = res.group(2)
        elif 'от' in vac_dict['salary']:
            res = re.search(r'([\d]+\D*[\d]*) ',vac_dict['salary'])
            vac_dict['min_salary'] = res.group(1)
            
        elif 'до' in vac_dict['salary']:
            res = re.search(r'([\d]+\D*[\d]*) ',vac_dict['salary'])
            vac_dict['max_salary'] = res.group(1)
            
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
        vacancies = vacancies.append(vac_dict, ignore_index = True)
    return(vacancies)
        


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
    result = pd.DataFrame()
    result = page_data(soup)
    print(f'страница {1} добавлена')
    pager_block = soup.find('div', {'data-qa':'pager-block'})
    next_page_tail = pager_block.find('a', {'data-qa':'pager-next'})
    i  = 2 
    while next_page_tail:
        soup = bs(requests.get(url+next_page_tail['href'], headers = headers).text, 'lxml')
        result = result.append(page_data(soup), ignore_index = True)
        pager_block = soup.find('div', {'data-qa':'pager-block'})
        next_page_tail = pager_block.find('a', {'data-qa':'pager-next'})
        print(f'страница {i} добавлена')
        i = i + 1
    return(result)
    

df = scrap_hh(link, 'data scientist', 1).loc[:, ['name','city', 'min_salary', 'max_salary', 'currency', 'link', 'source']]

print(df)