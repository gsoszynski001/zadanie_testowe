#!/usr/bin/env python3
import os
import re
import subprocess
import time
from os import system, name
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

def clear(): 
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

# Na różnych maszynach można spotkać różne versje Chroma.
# Zanim uruchomię test/skrypt sprawdzam jaką aktualnie wersję przeglądarki ma użytkownik i wybieram odpowiednią wersję driver'a
def getChromeVersion():
    p = subprocess.Popen(["powershell","$(Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe').'(Default)').VersionInfo"],stdout=subprocess.PIPE)
    result = p.communicate()
    r = re.search(r'^\D*(\d+)\.\d+\.?\d?\.?\d*.*$', str(result))
    return str(r.group(1))

value = input('Please choose driver:' + 
                    '\n\tFor "Chrome" press: 1' +
                    '\n\tFor "Firefox" press: 2' + 
                    '\n\tFor "Opera" press: 3' +
                    '\n\tFor "InternetExplorer" press: 4\n\t')
clear()

# Do skryptu dołączam drivery tak na wszelki wypadek gdyby w PATH'ie nie było odpowiednich ścieżek
# Użytkownik uruchamiający skrypt musi jedynie zadbać o to aby obok bieżącego pliku znalazł się katalog z driverami
PATH_TO_DRIVERS = os.getcwd()+ os.sep + "WebDrivers"

# Wzorzec "Page Object Pattern"
# Przy tak małym skrypcie właściwie do pominięcia jednakże przy większych projektach OBOWIĄKOWY
SEARCH_INPUT_SELECTOR                    = "input[type='search']"
POPUP_NOTIFICATION_CLOSE_BUTTON_SELECTOR = "button[data-role='close-and-accept-consent']"
SEARCH_BUTTON_SELECTOR                   = "button[type='submit'][data-role='search-button']"
FILTER_BLACK_COLOR_CHECKBOX_SELECTOR     = "//div[@data-box-name='Filtry']//label/span[text()='czarny']"
ARTICLE_SELECTOR                         = "div[data-analytics-category='allegro.listing'] article"
PRICE_SELECTOR                           = "div[class='_9c44d_3AMmE'] span[class='_1svub _lf05o']"

# Na podstawie preferencji użytkownika wybieram odpowiedni driver
if value == '1':
    version = getChromeVersion()
    if version == '85':
        path_to_chrome_driver = PATH_TO_DRIVERS + os.sep + "chromedriver_v85.exe"
    elif version == '86':
        path_to_chrome_driver = PATH_TO_DRIVERS + os.sep + "chromedriver_v86.exe"
    elif version == '87':
        path_to_chrome_driver = PATH_TO_DRIVERS + os.sep + "chromedriver_v87.exe"
    else:
        print("Not supported Chrome in " + version + " version!")
        exit()

    driver = webdriver.Chrome(executable_path=path_to_chrome_driver)
elif value == '2':
    path_to_firefox_driver = PATH_TO_DRIVERS + os.sep + "geckodriver.exe"
    driver = webdriver.Firefox(executable_path=path_to_firefox_driver)
elif value == '3':
    path_to_opera_driver = PATH_TO_DRIVERS + os.sep + "operadriver.exe"
    driver = webdriver.Opera(executable_path=path_to_opera_driver)
elif value == '4':
    path_to_ie_driver = PATH_TO_DRIVERS + os.sep + "IEDriverServer.exe"
    driver = webdriver.Ie(executable_path=path_to_ie_driver)
else:
    print("You have choosen not supported option!")
    exit()

# WŁAŚCIWY SCRYPT
try:
    driver.maximize_window()
    # 1. wchodzimy na strone www.allegro.pl
    driver.get('http://www.allegro.pl')
    wait = WebDriverWait(driver, 10, poll_frequency=1, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException])

    search_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_SELECTOR)))
    try:
        search_element.click()
    except ElementClickInterceptedException as error:
        driver.find_element_by_css_selector(POPUP_NOTIFICATION_CLOSE_BUTTON_SELECTOR).click()
        
    # 2. wpisujemy w wyszukiwarke Iphone 11
    search_element.send_keys("Iphone 11")

    search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_BUTTON_SELECTOR)))
    search_button.click()

    # 3. wybieramy kolor czarny
    black_color_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, FILTER_BLACK_COLOR_CHECKBOX_SELECTOR)))
    scrollElementIntoMiddle = ('var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);' +
                              'var elementTop = arguments[0].getBoundingClientRect().top;' +
                              'window.scrollBy(0, elementTop-(viewPortHeight/2));')
    driver.execute_script(scrollElementIntoMiddle, black_color_checkbox)
    
    try:
        black_color_checkbox.click()
    except (StaleElementReferenceException, ElementNotInteractableException) as error:
        black_color_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, FILTER_BLACK_COLOR_CHECKBOX_SELECTOR)))
        black_color_checkbox.click()

    # 4. zliczamy ilość wyświetlonych telefonów na pierwszej stronie wyników i ilość prezentujemy w consoli
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ARTICLE_SELECTOR)))
    results = driver.find_elements(By.CSS_SELECTOR, ARTICLE_SELECTOR)

    print("Ilosc wynikow na pierwszej stronie wyszukiwania: " + str(len(results)))

    # 5. szukamy największej ceny na liście i wyświetlamy w konsoli
    tmp_price = 0.0
    for r in results:
        price = r.find_element(By.CSS_SELECTOR, PRICE_SELECTOR).text
        price = price.replace('zł', '').replace(' ', '').replace(',', '.')
        price = float(price)
        if price > tmp_price:
            tmp_price = price

    print("Cena najdrozszego produktu: " + str(tmp_price))
    
    # 6. do największej ceny dodajemy 23%
    print("Cena najdrozszego produktu po dodaniu 23%: " + str(tmp_price * 1.23))
finally:
    driver.close()
