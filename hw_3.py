from pymongo import MongoClient
from pymongo.errors import *
import json

client = MongoClient('localhost', 27017)
db = client['vacancies']
vacancies = db.vacancies
duplicates = db.duplicates


with open('vacancies.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

#Создадим свой id. Уникальные записи запишем в vacancies, всё остальное в duplicates.
count = 0
for vacancy in data:
    vacancy['_id'] = vacancy['name'] + '/' + vacancy['company']
    try:
        vacancies.insert_one(vacancy)
    except:
        vacancy['_id'] = vacancy['name'] + '/' + vacancy['company'] + ' ' + str(count)
        duplicates.insert_one(vacancy)
        count += 1

#Посмотрим сколько всего документов и дубликатов
print(f'Всего документов: {vacancies.count_documents({})}')
print(f'Всего дубликатов: {duplicates.count_documents({})}')

#Этим запросом я произвела замену значения
filter = {"salary_min": None}
newvalues = { "$set": { "salary_min": 0 } }
vacancies.update_many(filter, newvalues)

#Этим запросом я удалила ссылку для мобильных устройств.
filter = {}
newvalues = {"$unset": {"link_for_mobile": 1}}
vacancies.update_many(filter, newvalues)

#Этим запросом я отфильтровала вакансии по ключевым словам, исключив "созвучную" вакансию.
query = vacancies.find({"$and": [{"$or": [{"name": {"$regex": ".*data", "$options": "i"}},
                                     {"name": {"$regex": ".*engineer", "$options": "i"}},
                                     {"name": {"$regex": ".*данных", "$options": "i"}},
                                     {"name": {"$regex": ".*дата", "$options": "i"}}]},
                                      {"name": {"$not": {"$regex": ".*scien.*", "$options": "i"}}}]}
                       ).sort({"salary_max": -1, "salary_min": -1})
count = 0
for doc in query:
    count += 1
    print(doc)

#Проверим, сколько осталось документов после фильтрации.
print(f'Осталось документов: {count}')

#Удалим удалим все дубликаты из коллекции и убедимся в этом.
duplicates.delete_many({})
print(f'Всего дубликатов: {duplicates.count_documents({})}')