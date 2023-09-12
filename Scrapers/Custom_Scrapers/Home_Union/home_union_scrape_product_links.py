from selenium import webdriver 
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


import pandas as pd

import time
import re
import csv

from selenium.webdriver.common.by import By

root = "https://homeunionnyc.com/collections/all"
page = 1
website_template = root + "?page={page}"

driver = webdriver.Chrome()  # Initialize the webdriver outside of the loop

links = []  # Initialize the links list outside the loop


data = {'title':[], 'price':[], 'condition':[], 'width':[], 'height':[], 'depth':[], 'description':[], 'tags':[], 'images':[]}

for page in range(1, 104):  
    website = website_template.format(page=page)
    driver.get(website)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(("xpath", '//div//div[@class="items"]')))

    main_container = driver.find_element("xpath", '//div[@class="items"]')
    all_items = main_container.find_elements("xpath", './/a')

    for item in all_items:
            try:
                div = item.find_element("xpath",'.//div[@class="absolute top--0 right--0 pt2 pr2 z2"]')
            except NoSuchElementException:
                # if no such div is found within the anchor, print href attribute
                links.append(item.get_attribute('href'))
                print("done scraping link" + item.get_attribute('href'))

# Write the links to a CSV file
with open('links_HomeUnion.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for link in links:
        writer.writerow([link])


