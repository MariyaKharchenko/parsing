import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime, time, timedelta
import time
import re
import json
#from fake_useragent import UserAgent
import pprint


params = {"L_save_area": "true",
          "items_on_page": 50,
          "hhtmFrom": "vacancy_search_filter",
          "search_field": "name",
          "search_field": "company_name",
          "search_field": "description",
          "enable_snippets": "false",
          "experience": "noExperience",
          "text": "data"+"engineer",
          "page": 0
}
url = "https://hh.ru"
#ua = UserAgent()
headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"}

session = requests.session()

vacancies = []

while True:
    response = session.get(url+'/search/vacancy', headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = json.loads(soup.find('template', attrs={'id': 'HH-Lux-InitialState'}).text)
    if not data['vacancySearchResult']['vacancies']:
        break

    for v in data['vacancySearchResult']['vacancies']:
        vacancy = {}

        vacancy['name'] = v['name']
        vacancy['link_for_desktop'] = v['links']['desktop']
        vacancy['link_for_mobile'] = v['links']['mobile']
        try:
            vacancy['salary_min'] = v['compensation']['from']
        except:
            vacancy['salary_min'] = None
        try:
            vacancy['salary_max'] = v['compensation']['to']
        except:
            vacancy['salary_max'] = None
        try:
            vacancy['currency'] = v['compensation']['currencyCode']
        except:
            vacancy['currency'] = None
        vacancy['company'] = v['company']['name']
        vacancies.append(vacancy)

    time.sleep(2)
    params['page'] += 1
with open('vacancies.json', 'a') as f:
    json.dump(vacancies, f)

