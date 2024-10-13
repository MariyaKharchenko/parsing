import requests
from lxml import html
import csv

headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'}
url = 'https://news.mail.ru/'

try:
    response = requests.get(url, headers=headers)

    #Заберем html дерево и вытащим из него нужные нам ссылки
    #(на момент написания кода на сайте их 11, нам нужно столько же)
    dom = html.fromstring(response.text)
    links = dom.xpath("//div[@data-logger='news__MainTopNews']//@href")
    print(len(links))

    #Возьмем дерево с каждой ссылки и заберем с него только то, что нам нужно
    #(заголовок новости и краткое описание). Запишем это в словарь. И добавим
    #все такие словари в список.
    news = []
    for link in links:
        try:
            response = requests.get(link, headers=headers)
            dom = html.fromstring(response.text)
            new = {}
            news_title = dom.xpath("//header/h1/text()")
            news_p = dom.xpath("//header//p/text()")[0]

            new['news_title'] = news_title[0]
            new['news_p'] = ' '.join(news_p.split())

            news.append(new)
        except requests.exceptions.HTTPError as e:
            print("Response not 200:", e)

    #Запишем данные в csv файл.
    field_names = ['news_title', 'news_p']
    with open("news.csv", "w", encoding='utf8') as w_file:
        writer = csv.DictWriter(w_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(news)

except requests.exceptions.HTTPError as e:
    print("Response not 200:", e)

