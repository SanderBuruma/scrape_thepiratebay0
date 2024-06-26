from time import sleep
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from datetime import datetime, timedelta
from helpers.driver import get_chrome_driver, wait_for_element, wait_for_partial_name, wait_for_and_click
import os
import json


# Retrieve previous torrents
filename = 'torrents.csv'
file_contents = ''
if os.path.exists(filename):
    with open(filename, 'r') as f:
        file_contents = f.read()
file_lines = file_contents.split('\n') if file_contents else []


driver: WebDriver = get_chrome_driver(headless=True)

# load cookies if possible
driver.get('https://thepiratebay0.org/')
if os.path.exists('cookies.json'):
    wait_for_element(driver, By.XPATH, '/html')
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)


hash_ = ''
for i in range(100, 1, -1):
    url = 'https://thepiratebay0.org/browse/401/{0}/3'.format(i)
    driver.get(url)

    # Wait for the driver to finish loading the new page by only continuing when the hash changes
    sr = wait_for_element(driver, By.XPATH, '//*[@id="searchResult"]')
    while (hash(sr.get_attribute('innerHTML')) == hash_):
        sleep(.02)
        sr = wait_for_element(driver, By.XPATH, '//*[@id="searchResult"]')
    hash_ = hash(sr.get_attribute('innerHTML'))

    # Get the name and seed count elements of the torrents
    elements = driver.find_elements(By.XPATH, '//*[@id="searchResult"]/tbody/tr/td[2]/div/a')
    seeders = driver.find_elements(By.XPATH, '//*[@id="searchResult"]/tbody/tr/td[3]')

    # Generate the csv file addition
    i = 0
    for e in elements:
        num_seeders = int(seeders[i].get_attribute('innerHTML'))
        name = e.get_attribute('innerHTML')
        name = ' '.join(name.split(';'))
        if (num_seeders < 9 or num_seeders > 999):
            i+=1
            continue

        # Don't record adult content
        if any([word in name.lower() for word in ['cunt', 'sex', 'dick', 'furry', 'titt', 'lust', 'shameless', 'stepmom', 'milf', 'lewd']]):
            i+=1
            continue

        file_lines.append(name + ';' + e.get_attribute('href'))
        i+=1

# Delete duplicates
file_lines = list(set(file_lines))

# Save the file
csv = '\n'.join(file_lines)
with open(filename, 'w') as f:
    f.write(csv)

# Save cookies
cookies = driver.get_cookies()
with open('cookies.json', 'w') as f:
    json.dump(cookies, f)