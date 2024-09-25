import requests
import json
import os
import requests
from dotenv import load_dotenv
from pprint import pprint

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Конечная точка API
endpoint = "https://api.foursquare.com/v3/places/search"

# Определение параметров для запроса API
category = input("Введите название интересующей Вас категории на английском языке (например: Park, Museums и т.п.): ")
params = {
    'limit': 15,
    'query': category,
    'fields': 'name,location,rating'
}

headers = {
    "Accept": "application/json",
    "Authorization": os.getenv("API_KEY")
}

# Отправка запроса API и получение ответа
response = requests.get(endpoint, params=params,headers=headers)

# Проверка успешности запроса API
if response.status_code == 200:
    print("Успешный запрос API!")
    data = json.loads(response.text)
    establishments = []
    for place in data['results']:
        place_name = place.get('name')
        place_address = place.get('location')['formatted_address']
        place_rating = place.get('rating') if 'rating' in place else "Рейтинг не определялся"
        establishments.append({'name': place_name, 'address': place_address, 'rating': place_rating})
    for establishment in establishments:
        print()
        print(f"Название: {establishment['name']}")
        print(f"Адрес: {establishment['address']}")
        print(f"Рейтинг: {establishment['rating']}")

else:
    print("Запрос API завершился неудачей с кодом состояния:", response.status_code)
    print(response.text)
