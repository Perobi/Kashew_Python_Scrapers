from selenium import webdriver 
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import re
import csv
from selenium.webdriver.common.by import By
import pandas as pd 

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
with open('./links_HomeUnion.csv', 'r') as file:
    # Create a CSV reader
    reader = csv.reader(file)

    # Loop through each row in the CSV
    for row in reader:
        # Each row is a list of strings. In this case, there is only one string in the list.
        link = row[0]
        # loop through each link

        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(("xpath", '//div[@class="product"]')))
        product_container = driver.find_element("xpath", '//div[@class="product"]')

        # Initialize empty values for each key in the data dictionary
        item_data = {key: '' for key in data.keys()}

        # Get the title ---------------
        try: 
            title = product_container.find_element("xpath", './/h1').text
        except NoSuchElementException:
            title = ''
        item_data['title'] = title

        # Get the price ---------------
        try: 
            price_container = product_container.find_element("xpath", './/div[@data-price-wrapper]')
            price = price_container.find_element("xpath", './/span[@data-product-price]').text
        except NoSuchElementException:
            price = ''

        item_data['price'] = price

        # RETAIL PRICE
        try: 
            retail_price = price_container.find_element("xpath", './/s[@data-compare-price]')
            item_data['retail_price'] = retail_price.text
        except NoSuchElementException:
            item_data['retail_price'] = ''

        # Get the condition ---------------
        item_data['condition'] = "Excellent"

        # Get the dimensions ---------------
        product_description = product_container.find_element("xpath", './/div[@data-product-description]')

        try: 
            strong_element = product_description.find_element("xpath", './/strong')
            dimensions_text = strong_element.text

            # Define patterns for wide (width), deep (depth), and tall (height)
            patterns = {
                'width': r"(\d+\.?\d*)\"\s*wide",
                'height': r"(\d+\.?\d*)\"\s*tall",
                'depth': r"(\d+\.?\d*)\"\s*deep",
            }

            # For each dimension, find the number preceding its descriptor and add it to the data dictionary
            for dimension, pattern in patterns.items():
                match = re.search(pattern, dimensions_text)
                if match:
                    # If a match is found, add it to the data dictionary
                    item_data[dimension] = match.group(1)
                else:
                    # If no match is found, append an empty string or None
                    item_data[dimension] = ''
        except NoSuchElementException:
            item_data['width'] = ''
            item_data['height'] = ''
            item_data['depth'] = ''

        # Get the description ---------------
        try: 
            # Get all the <p> elements within the product description
            p_elements = product_description.find_elements("xpath", './/p')

            # Ensure that at least two <p> elements were found before trying to access them
            if len(p_elements) >= 2:
                description = p_elements[1].text
            else:
                description = ''
        except NoSuchElementException:
            description = ''

        # Append the description to the appropriate list
        item_data['description'] = description

        try: 
            # Images ---------------
            img_container = product_container.find_element("xpath", './/div[@data-product-thumbnails]')
            images = img_container.find_elements("xpath", './/img')
            image_sources = []
            for image in images:
                image_src = image.get_attribute('src').replace('_300x', '')
                image_sources.append(image_src)
            # Join all image sources for a single product with a delimiter
            item_data['images'] = ','.join(image_sources)
        except NoSuchElementException:
            item_data['images'] = ''

        # sku ---------------
        try: 
            meta_tag = product_container.find_element("xpath", './/meta[@itemprop="image"]')
            content = meta_tag.get_attribute('content')
            sku = content.split('v=')[-1]  # This will split the string on 'v=' and get the last part (i.e., what comes after 'v=')
        except NoSuchElementException:
            sku = ''
        # Append the SKU to the appropriate list
        item_data['sku'] = sku

        # Append the item data to the respective lists in the main data dictionary
        for key in data.keys():
            data[key].append(item_data[key])

        print("finished scraping " + title)

# Once the loop is done, convert your dictionary into a pandas DataFrame
df = pd.DataFrame(data)

# Finally, write your DataFrame to a CSV file
df.to_csv('home_union_scraped_data.csv', index=False)

driver.quit()