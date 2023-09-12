from selenium import webdriver 
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import csv
from selenium.webdriver.common.by import By
import pandas as pd 

import os

# Get the current script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))

# Change the working directory to the script's directory
os.chdir(script_directory)

def clean_url(url):
    return re.sub(r'_\d+x\d+_crop_center', '', url)

driver = webdriver.Chrome()  # Initialize the webdriver outside of the loop

data = {
    "sku": [],
    'title': [],
    'price': [],
    'retail_price': [],
    'condition': [],
    'width': [],
    'height': [],
    'depth': [],
    'description': [],
    'tags': [],
    'images': []
}

# Open the CSV file
with open('./DallasFurnitureLinks.csv', 'r') as file:
    # Create a CSV reader
    reader = csv.reader(file)
    # Loop through each row in the CSV
    for row in reader:
       
        # Each row is a list of strings. In this case, there is only one string in the list.
        link = row[0]
        # loop through each link
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(("xpath", '//section[@class="product--container"]')))
            product_container = driver.find_element("xpath", '//section[@class="product--container"]')
            # Initialize empty values for each key in the data dictionary
            item_data = {key: '' for key in data.keys()}

            # Get the title ---------------
            try: 
                title = product_container.find_element("xpath", './/h1[@class="product-title"]').text
                # Extract possible dimensions from the title
                possible_dimensions = re.findall(r'(\d+\"|\d+\.\d+\")', title)
                if len(possible_dimensions) == 1:
                    item_data['height'] = possible_dimensions[0].replace("\"", "")
                elif len(possible_dimensions) == 2:
                    item_data['height'] = possible_dimensions[0].replace("\"", "")
                    item_data['width'] = possible_dimensions[1].replace("\"", "")
            except NoSuchElementException:
                title = ''
            item_data['title'] = title

            # Get the price ---------------
            try: 
                price_container = product_container.find_element("xpath", './/div[@data-product-pricing]')
                price = price_container.find_element("xpath", './/span[@data-price]').text
            except NoSuchElementException:
                price = ''
            item_data['price'] = price

            # RETAIL PRICE
            try: 
                retail_price_container = price_container.find_element("xpath", './/div[@data-price-compare-container]')
                retail_price = retail_price_container.find_element("xpath", './/span[@data-price-compare]')
                item_data['retail_price'] = retail_price.text
            except NoSuchElementException:
                item_data['retail_price'] = ''

            # Get the condition ---------------
            item_data['condition'] = "Very Good"

            # Get the description ---------------
            try:
                description_container = product_container.find_element("xpath", '//div[@class="product-description rte"]')
                description = description_container.find_element("xpath", './p').text
            except NoSuchElementException:
                description = ''
            item_data['description'] = description

            # Get the dimensions
            try:
                dimensions_container = product_container.find_element("xpath", '//div[@class="product-description rte"]')
                paragraphs = dimensions_container.find_elements("xpath", './p')

                # Initialize the dimensions if they have not been found in the title
                if not item_data['width']:
                    item_data['width'] = ''
                if not item_data['height']:
                    item_data['height'] = ''
                if not item_data['depth']:
                    item_data['depth'] = ''

                # Go through each paragraph and assign dimensions accordingly
                for paragraph in paragraphs:
                    dimensions = paragraph.text.split('x')
                    for dim in dimensions:
                        dim = dim.strip()
                        # Extract the numerical part of the dimension, keeping decimal points
                        numeric_part = "".join(ch for ch in dim if ch.isdigit() or ch == '.')

                        if 'W' in dim and not item_data['width']:
                            item_data['width'] = numeric_part
                        elif 'H' in dim and not item_data['height']:
                            item_data['height'] = numeric_part
                        elif 'D' in dim and not item_data['depth']:
                            item_data['depth'] = numeric_part

            except NoSuchElementException:
                pass

            # Get the images and SKU
            try:
                images_container = product_container.find_element("xpath", '//div[@class="gallery-navigation--scroller"]')
                images_elements = images_container.find_elements("xpath", './/img')
                
                images = []
                sku = None
                for image in images_elements:
                    image_src = image.get_attribute('src')
                    
                    cleaned_image_src = clean_url(image_src)
                    images.append(cleaned_image_src)
                    
                    # Extract SKU
                    if '?v=' in image_src and not sku:
                        sku = image_src.split('?v=')[1]

            except NoSuchElementException:
                images = []
                sku = None

            # Convert the list of images into a single string
            image_string = ', '.join(images)
            item_data['images'] = image_string
            item_data['sku'] = sku

            for key in item_data:
                data[key].append(item_data[key])
            print(item_data)

        except TimeoutException:
            print(f'TimeoutException occurred for URL: {link}')
            continue

# Once the loop is done, convert your dictionary into a pandas DataFrame
df = pd.DataFrame(data)

# Finally, write your DataFrame to a CSV file
df.to_csv('dallas_furniture_bank.csv', index=False)
print("Done")

driver.quit()
