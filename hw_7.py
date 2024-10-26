from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from fake_useragent import UserAgent


ua = UserAgent()
options = Options()
options.add_argument('start-maximized')
time.sleep(5)
driver = webdriver.Chrome(options=options)
driver.get('https://auto.drom.ru/')
stealth(driver, user_agent=ua.random, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True, )

#Выберем марку, модель и "год от" для авто.
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='css-75hx9m e1a8pcii0']/input")))
drop_down_brand = driver.find_element(By.XPATH, "//div[@class='css-75hx9m e1a8pcii0']/input")
drop_down_brand.click()
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='css-1h3i1m2 e1x0dvi11'][contains(text(), 'Toyota')]")))
brand = driver.find_element(By.XPATH, "//div[@class='css-1h3i1m2 e1x0dvi11'][contains(text(), 'Toyota')]")
brand.click()
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='css-13306mq e1207tlp0']")))
drop_down_model = driver.find_element(By.XPATH, "//input[@class='css-13306mq e1207tlp0']")
drop_down_model.click()
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='css-1vv9lau e1x0dvi11'][contains(text(), 'Alphard')]")))
model = driver.find_element(By.XPATH, "//div[@class='css-1vv9lau e1x0dvi11'][contains(text(), 'Alphard')]")
model.click()
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='css-njjn28 e75dypj1'][contains(text(), 'Год от')]")))
year_button = driver.find_element(By.XPATH, "//button[@class='css-njjn28 e75dypj1'][contains(text(), 'Год от')]")
year_button.click()
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='css-1vv9lau e1x0dvi11'][contains(text(), '2022')]")))
year = driver.find_element(By.XPATH, "//div[@class='css-1vv9lau e1x0dvi11'][contains(text(), '2022')]")
year.click()

#Нажмем на кнопку "Показать".
WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-ftid='sales__filter_submit-button']")))
submit_button = driver.find_element(By.XPATH, "//button[@data-ftid='sales__filter_submit-button']")
submit_button.click()
time.sleep(60)

while True:
    try:
        #Полученим HTML-код страницы
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        #Извлечем информацию об автомобилях, значение класса подберем в зависимости от того, какая загрузится страница.
        cars = soup.find_all('div', ('class', 'css-1f68fiz ea1vuk60'))
        cars_alt = soup.find_all('div', ('class', 'css-eyz1wk e6ttj1f0'))
        if cars:
            cars = cars
        elif cars_alt:
            cars = cars_alt
        data = []
        for car in cars:
            #Когда работаем с HTML-кодом, WebDriverWait не работает, что логично. Далее используем time.sleep
            time.sleep(60)
            #Найдем ссылку на вто и кликнем по ней.
            link = car.find('a', ('class', 'g6gv8w4 g6gv8w8 _1ioeqy90')).get('href')
            time.sleep(5)
            driver.find_element(By.XPATH, f"//a[@href='{link}']").click()
            try:
                time.sleep(60)
                html_car = driver.page_source
                time.sleep(60)
                soup_car = BeautifulSoup(html_car, 'html.parser')

                #Определим статус авто
                preorder = soup_car.find(string=lambda text: text.startswith("под"))
                sold = soup_car.find(string=lambda text: text.endswith("закрыты"))

                #Если авто в архиве - уйдем из цикла
                if preorder:
                    status = 'Под заказ'
                    print('Под заказ')
                elif sold:
                    print('break')
                    break
                else:
                    print('Актуально')
                    status = 'Актуально'

                #Соберем остальные данные по авто
                try:
                    title = soup_car.find('span', ('class', 'css-1kb7l9z e162wx9x0')).text.strip()
                    price = ''.join(c for c in (soup_car.find('div', ('class', 'wb9m8q0')).text) if c.isdigit())
                    gearbox = soup_car.find(string=lambda text: text.startswith("Коробка")).parent.parent.find(
                        'td').text.strip()
                    gear = soup_car.find(string=lambda text: text.startswith("Привод")).parent.parent.find(
                        'td').text.strip()
                    power = str(''.join(c for c in (soup_car.find('span', ('class', 'css-9g0qum e162wx9x0')).text) if
                                        c.isdigit()) + 'лс')
                except:
                    title = soup_car.find('title').text.split(',')[0]
                    price = None
                    gearbox = None
                    gear = None
                    power = None

                #И добавим их в data
                data.append([title, price, gearbox, gear, power, status, link])
            except Exception as e:
                print(f"Ошибка: {e}")
                driver.back()

            #Это переход на предыдущую страницу...
            driver.back()


    except Exception as e:
        print(f"Ошибка: {e}")


    finally:
        #Наконец, запишем данные в csv-файл.
        with open('cars2.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Название', 'Цена', 'Коробка передач', 'Привод', 'Мощность', 'Статус', 'Ссылка'])
            writer.writerows(data)

            print("Данные успешно записаны в файл cars2.csv")
        driver.quit()
