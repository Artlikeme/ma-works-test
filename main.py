# from selenium import webdriver
# from selenium.common import NoSuchElementException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# import csv
#
# from selenium.webdriver.support.wait import WebDriverWait
#
#
# def parse_site(url):
#     options = Options()
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_argument('--disable-infobars')
#     options.add_argument('--start-maximized')
#     options.add_argument('--disable-extensions')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--ignore-certificate-errors')
#     options.add_argument(
#         '--user-agent=Mozilla/5.0 '
#         '(Windows NT 10.0; Win64; x64) '
#         'AppleWebKit/537.36 (KHTML, like Gecko) '
#         'Chrome/58.0.3029.110 Safari/537.3')
#     driver = webdriver.Chrome(options=options)
#
#     with open('products.csv', 'w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerow(["id", "name", "link", "regular_price", "promo_price", "brand"])
#         for pagination in range(2, 12):
#             driver.get(url)
#
#             # Ожидание загрузки страницы
#             WebDriverWait(driver, 5)
#
#             # Получение всех товаров
#             products = driver.find_elements(By.CLASS_NAME, "subcategory-or-type__products-item")
#             for i in range(len(products)):
#                 # Получаем товары
#                 products = driver.find_elements(By.CLASS_NAME, "subcategory-or-type__products-item")
#                 product = products[i]
#
#                 # Исключаем товары, которые уже раскупили
#                 try:
#                     if product.find_element(By.CLASS_NAME, "catalog-2-level-product-card__title").text == "Раскупили":
#                         continue
#                 except NoSuchElementException:
#                     pass
#                 # Создаем нужные нам переменные
#                 id = product.get_attribute("data-sku")
#                 name = product.find_element(By.CLASS_NAME, 'catalog-2-level-product-card__name').get_attribute('title')
#                 try:
#                     promo_price = product.find_element(By.CLASS_NAME,
#                                                        'product-price__sum-rubles').text + product.find_element(
#                         By.CLASS_NAME, 'product-price__sum-penny').text
#                 except NoSuchElementException:
#                     promo_price = product.find_element(By.CLASS_NAME, 'product-price__sum-rubles').text
#                 try:
#                     product.find_element(By.CLASS_NAME, 'product-card-photo__discount')
#                     flag = True
#                 except NoSuchElementException:
#                     flag = False
#                 try:
#                     if flag:
#                         regular_price = product.find_element(
#                             By.CLASS_NAME, 'product-unit-prices__old-wrapper').find_element(
#                             By.CLASS_NAME, 'product-price__sum-rubles').text + product.find_element(
#                             By.CLASS_NAME, 'product-unit-prices__old-wrapper').find_element(
#                             By.CLASS_NAME, 'product-price__sum-penny').text
#                     else:
#                         regular_price = promo_price
#                         promo_price = 0
#                 except NoSuchElementException:
#                     if flag:
#                         regular_price = product.find_element(
#                             By.CLASS_NAME, 'product-unit-prices__old-wrapper').find_element(
#                             By.CLASS_NAME, 'product-price__sum-rubles').text
#                     else:
#                         regular_price = promo_price
#                         promo_price = 0
#                 link = product.find_element(
#                     By.CLASS_NAME, 'catalog-2-level-product-card__name').get_attribute("href")
#                 # Переход на страницу объекта для получения brand
#                 driver.get(link)
#                 brand = driver.find_element(By.CLASS_NAME, "product-attributes__list-item-link").text
#                 driver.back()
#                 # Запись в csv
#                 writer.writerow([id, name, link, regular_price, promo_price, brand])
#             # Изменение url для след итерации
#             url = f"https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?from=under_search&page={pagination}"
#     driver.quit()
#
# parse_site('https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?from=under_search')
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def set_price(product):
    try:
        promo_price = product.find_element(By.CLASS_NAME,
                                           'product-price__sum-rubles').text + product.find_element(
            By.CLASS_NAME, 'product-price__sum-penny').text
    except Exception:
        promo_price = product.find_element(By.CLASS_NAME, 'product-price__sum-rubles').text
    try:
        product.find_element(By.CLASS_NAME, 'product-card-photo__discount')
        flag = True
    except NoSuchElementException:
        flag = False
    try:
        if flag:
            regular_price = product.find_element(
                By.CLASS_NAME, 'product-unit-prices__old-wrapper').find_element(
                By.CLASS_NAME, 'product-price__sum-rubles').text + product.find_element(
                By.CLASS_NAME, 'product-unit-prices__old-wrapper').find_element(
                By.CLASS_NAME, 'product-price__sum-penny').text
        else:
            regular_price = promo_price
            promo_price = 0
    except NoSuchElementException:
        if flag:
            regular_price = product.find_element(
                By.CLASS_NAME, 'product-unit-prices__old-wrapper').find_element(
                By.CLASS_NAME, 'product-price__sum-rubles').text
        else:
            regular_price = promo_price
            promo_price = 0
    return regular_price, promo_price


def set_brand(link):
    response = requests.get(link)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        brand_element = soup.find(class_='product-attributes__list-item-link')
        brand = brand_element.get_text()
    else:
        brand = "Unknown"
    return brand


def parse_site(url):
    options = Options()
    options.add_argument(
        '--user-agent=Mozilla/5.0 '
        '(Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/58.0.3029.110 Safari/537.3')

    with webdriver.Chrome(options=options) as driver:
        with open('products.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "link", "regular_price", "promo_price", "brand"])

            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "subcategory-or-type__products-item")))

            # for pagination in range(2, 12):
            #     # Получение всех товаров
            #     products = driver.find_elements(By.CLASS_NAME, "subcategory-or-type__products-item")
            #     for product in products:
            #         # Проверка на наличие элемента "Раскупили"
            #         if product.find_elements(By.CLASS_NAME, "catalog-2-level-product-card__title") and \
            #                 product.find_element(By.CLASS_NAME, "catalog-2-level-product-card__title").text == "Раскупили":
            #             continue
            #
            #         id = product.get_attribute("data-sku")
            #         name = product.find_element(By.CLASS_NAME, 'catalog-2-level-product-card__name').get_attribute(
            #             'title')
            #         # Обработка цен
            #         regular_price, promo_price = set_price(product)
            #
            #         link = product.find_element(By.CLASS_NAME, 'catalog-2-level-product-card__name').get_attribute(
            #             "href")
            #         driver.get(link)
            #         brand = driver.find_element(By.CLASS_NAME, "product-attributes__list-item-link").text
            #         driver.back()
            #
            #         writer.writerow([id, name, link, regular_price, promo_price, brand])
            #
            #     # Изменение URL для следующей итерации
            #     url = f"https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?from=under_search&page={pagination}"
            #     driver.get(url)
            for pagination in range(2, 12):
                # Получение всех товаров
                products = driver.find_elements(By.CLASS_NAME, "subcategory-or-type__products-item")
                for product in products:
                    # Проверка на наличие элемента "Раскупили"
                    if product.find_elements(By.CLASS_NAME, "catalog-2-level-product-card__title") and \
                            product.find_element(By.CLASS_NAME,
                                                 "catalog-2-level-product-card__title").text == "Раскупили":
                        continue

                    id = product.get_attribute("data-sku")
                    name = product.find_element(By.CLASS_NAME, 'catalog-2-level-product-card__name').get_attribute(
                        'title')
                    # Обработка цен
                    regular_price, promo_price = set_price(product)

                    link = product.find_element(By.CLASS_NAME, 'catalog-2-level-product-card__name').get_attribute(
                        "href")
                    # Устанавливаем бренд
                    brand = set_brand(link)

                    writer.writerow([id, name, link, regular_price, promo_price, brand])

                # Изменение URL для следующей итерации
                url = f"https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?from=under_search&page={pagination}"
                driver.get(url)


parse_site('https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?from=under_search')
