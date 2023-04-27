import csv
import datetime
import time
from itertools import chain
import os
from data.headers import headers
from grab import Grab
from bs4 import BeautifulSoup

count = 0
start = time.time()
report_file_name = f'report/data_avito_{datetime.datetime.now().strftime("%Y.%m.%d")}.csv'

# Создаём список производителей
list_auto_temp = os.listdir('data_avito_parser/auto')
list_auto = []
for i in list_auto_temp:
    list_auto.append(i.split('.')[0])

print("-" * 60 + "\n" + "Список производителей: " + ", ".join(list_auto) + "\n" + "-" * 60)
for item_auto in list_auto:

    # Создаем список городов из файла 'data_avito_parser/city.csv'
    list_city = {}
    with open('data_avito_parser/city.csv', 'r', encoding='utf-8-sig') as file:
        temp_list_city = file.read().split('\n')

    for i in temp_list_city:
        list_city[i.split(',')[0]] = i.split(',')[1]

    print("-" * 60 + "\n" + "Список городов: " + ", ".join(list_city) + "\n" + "-" * 60)

    # Создаём список запчастей и файл с шапкой
    list_codes = []
    with open(f'data_avito_parser/auto/{item_auto}.csv', 'r', encoding='utf-8-sig') as file:
        temp_list_city = file.read().split('\n')
    for i in temp_list_city:
        list_codes.append(i)

    print("-" * 60 + "\n" + "Список запчастей: " + ", ".join(list_codes) + "\n" + "-" * 60)

    # Если это первая итерация, то создаем файл для отчета с шапкой таблицы
    if count == 0:
        try:
            list_table_headers = ['Производитель', 'Код запчасти', 'Наименование']
            for i in list_city:
                list_table_headers.append(f'{i} количество объявлений')
                list_table_headers.append(f'{i} минимальная цена')

            with open(report_file_name, 'w', encoding='utf-8-sig', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(
                    (
                        list_table_headers
                    )
                )
        except Exception as err:
            print("Возникла ошибка: \"{}\"".format(err))
            exit(-1)

    # Проходим по каждому коду запчасти и парсим
    for code in list_codes:

        # Сначала заходим по URL на страницу с результатами поиска по всей России. Ищем имя для товара))
        url = f'https://www.avito.ru/all?bt=1&q={code}&s=1'
        g = Grab(log_file=f'report/temp_file.html')
        g.setup(headers=headers)

        # Открываем созданный файл, чтобы из него забирать информацию
        with open(f'report/temp_file.html', 'r', encoding='utf-8-sig') as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        list_names = soup.findAll(
            class_='title-root-zZCwT iva-item-title-py3i_ title-listRedesign-_rejR title-root_maxHeight-X6PsH '
                   'text-text-LurtD text-size-s-BxGpL text-bold-SinUO')

        # Наименование товара берется из самого короткого названия в авито
        name = min(chain.from_iterable(list_names), key=len)

        # Создаем список, который будем наполнять данными перед вставкой в файл
        list_table_body = [item_auto, code, name]

        print(f'\n{item_auto} - {code} - {name}', end=' ')

        # Каждый товар пробегает по каждому городу и сохраняет инфу по ценам и количеству объявлений
        for city in list_city:
            print('*', end=' ')
            url = f'https://www.avito.ru/{list_city[city]}?bt=1&q={code}&s=1'

            try:
                g = Grab(log_file=f'report/temp_file.html')
                g.setup(headers=headers)
                g.go(url)
            except Exception as err:
                print("Возникла ошибка! Что то не так при переходе по ссылке: \"{}\"".format(err))
                print(url)

            # Чтение временного файла
            number_of_sellers = 0
            try:
                with open(f'report/temp_file.html', 'r', encoding='utf-8-sig') as file:
                    src = file.read()
                soup = BeautifulSoup(src, 'lxml')
                block = soup.find(class_='items-items-kAJAg')
                number_of_sellers = len(
                    block.findAll(class_='title-root-zZCwT iva-item-title-py3i_ title-listRedesign-_rejR '
                                         'title-root_maxHeight-X6PsH text-text-LurtD text-size-s-BxGpL '
                                         'text-bold-SinUO'))
            except Exception as err:
                print("Возникла ошибка, когда искали на сайте количество объявлений: \"{}\"".format(err))
                print(f'{item_auto} | {code} | {name} | {city} | {number_of_sellers}')
                print(url)

            # Если количество объявлений 0, то и минимальную цену ставим 0
            min_price = 0
            try:
                if number_of_sellers == 0:
                    min_price = 0
                else:
                    # Цикл на случай, если Цена не указана на товаре, берем цену у следующего товара по порядку
                    for i in range(number_of_sellers):
                        min_price = soup.findAll(class_='price-text-_YGDY text-text-LurtD text-size-s-BxGpL')[i].text
                        if min_price != 'Цена не указана':
                            break
                        else:
                            continue
            except Exception as err:
                print("Возникла ошибка, когда собирали данные по ценам на сайте: \"{}\"".format(err))
                print(f'{item_auto} | {code} | {name} | {city} | {number_of_sellers} | {min_price}')
                print(url)

            # Если в итоге товара с ценой нет, то ставим 0
            if min_price == 'Цена не указана':
                min_price = 0
            elif min_price != 0:
                try:
                    min_price = int(min_price.strip(' ₽').replace(' ', ''))
                except Exception as err:
                    print("Возникла ошибка, когда убирали знак ₽ из цены: \"{}\"".format(err))
                    print(f'{item_auto} | {code} | {name} | {city} | {number_of_sellers} | {min_price}')
                    print(url)
                    min_price = -1

            # Добавляем полученную информацию в список для вставки в файл
            list_table_body.append(number_of_sellers)
            list_table_body.append(min_price)

        # Записываем список в файл одной строкой и идем к следующему товару
        try:
            with open(report_file_name, 'a', encoding='utf-8-sig', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(
                    (
                        list_table_body
                    )
                )
        except Exception as err:
            print("Возникла ошибка при добавлении собранных данных в файл: \"{}\"".format(err))
            print(url)
            # time.sleep(1)
    count += 1
print(f'Конец. Время выполнения: {time.time() - start}')
