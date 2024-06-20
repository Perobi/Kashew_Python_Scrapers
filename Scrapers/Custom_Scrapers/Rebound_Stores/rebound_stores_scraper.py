import json

import subprocess
import csv
import os
import re
import html



try:
    import pandas as pd
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from urllib.parse import urlparse
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    subprocess.check_call(["pip", "install", "pandas"])
    subprocess.check_call(["pip", "install", "requests"])
    subprocess.check_call(["pip", "install", "urllib3"])
    subprocess.check_call(["pip", "install", "bs4"])
    import pandas as pd
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from bs4 import BeautifulSoup

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


base_url = "https://www.reboundstores.com"

# Setup
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'
}
pages = [1, 2, 3]
multiple = 243
directory_path = "/Users/perobiora/Desktop/Kashew/Kashew_Python_Scrapers/Output/"

# Unique URLs set
unique_urls = set()

title = []
sku = []
price = []
retail_price = []
description = []
width = []
height = []
depth = []
tags = []
brand_name = []
designer = []
imgs_urls = []


def extract_core_dimensions(dimension_text):
    # Clean up the text by replacing known issues
    dimension_text = dimension_text.replace('‚Äù', '"').replace('“', '"').replace('”', '"').strip()

    # Initialize dimensions
    width = None
    height = None
    depth = None

    # Define regex patterns to match dimensions more robustly
    pattern = r'(\d*\.?\d+)"?\s*(W|H|D)'

    # Find all matches in the dimension text
    matches = re.findall(pattern, dimension_text, re.IGNORECASE)

    # Process each match
    for value, dimension_type in matches:
        value = float(value)  # Convert value to float
        if dimension_type.upper() == 'W':
            width = value
        elif dimension_type.upper() == 'H':
            height = value
        elif dimension_type.upper() == 'D':
            depth = value

    return width, height, depth

def clean_description(text):
    # Common replacements and cleaning
    replacements = {
        '‚Äù': '"',  # Replace special quote with inches symbol
        '“': '"',
        '”': '"',
        '\u003c': '<',  # Decode HTML entities if any
        '\u003e': '>',
        '\n': ' ',  # Replace new lines with space
        '\r': '',
        '  ': ' '  # Replace double spaces with single space
    }
    
    # Apply replacements
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Optionally remove HTML tags if present
    text = re.sub(r'<[^>]+>', '', text)

    # Normalize white spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# # Session to maintain cookies, headers across requests
with requests.Session() as session:
    session.headers.update(headers)
    for page in pages:
        # Calculate the correct offset
        offset = (page - 1) * multiple
        # Construct the URL
        url = f"{base_url}/shop-now?offset={offset}" if offset > 0 else f"{base_url}/shop-now"

        # Fetch the page
        response = session.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Extracting product links
            products_container = soup.find('div', class_='products-flex-container')
            if products_container:
                links = products_container.find_all('a', href=True)
                for link in links:
                    unique_urls.add(base_url + link['href'])

        else:
            print(f"Failed to fetch page {page}: {response.status_code}")

# Printing or processing the unique URLs
print(f"Total unique URLs extracted: {len(unique_urls)}")


# Fetch and save the HTML content of the first URL
for url in list(unique_urls):
    response = requests.get(url, headers=headers)
    # save the html content to a file
    # file_name = url.split('/')[-1] + '.html'
    # full_path = directory_path + file_name
    # with open(full_path, 'w') as file:
    #     file.write(response.text)
    # print(f"HTML content saved to {full_path}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract the title and remove whitespace characters
        title_text = soup.find('h1', class_='ProductItem-details-title')
        if title_text:
            title_text = title_text.text.strip()
        else:
            title_text = soup.find('div', class_='grid-title')
            if title_text:
                title_text = title_text.text.strip()
            else:
                title_text = ""

        # Append the extracted title to the title list
        title.append(title_text)

        # Extract original price
        original_price = soup.find('meta', {'property': 'product:original_price:amount'})
        if original_price:
            original_price_amount = original_price.get('content').rstrip('0').rstrip('.')
            retail_price.append(original_price_amount)
        else:
            retail_price.append("")

        # Extract sale price
        sale_price = soup.find('meta', {'property': 'product:sale_price:amount'})
        if sale_price:
            sale_price_amount = sale_price.get('content').rstrip('0').rstrip('.')
            price.append(sale_price_amount)

        else:
            sale_price = soup.find('meta', {'property': 'product:price:amount'})
            if sale_price:
                sale_price_amount = sale_price.get('content').rstrip('0').rstrip('.')
                price.append(sale_price_amount)
            else:
                price.append("")

        # Extract SKU from JSON LD script tags
        script_tags = soup.find_all('script', type='application/ld+json')
        sku_found = False
        for script_tag in script_tags:
            # Extract JSON data
            try:
                json_data = json.loads(script_tag.string)
            except json.JSONDecodeError:
                continue  # Skip if JSON parsing fails
            
            # Extract SKU if 'offers' is present and has 'sku'
            if 'offers' in json_data and 'sku' in json_data['offers']:
                sk = json_data['offers']['sku']
                sku.append(sk)
                sku_found = True
                break  # Exit loop once SKU is found
        
        if not sku_found:
            sku.append("")  # Append empty string if SKU not found

        # Extract images
        img_urls = []
        image_div = soup.find('div', class_='ProductItem-gallery-thumbnails')
        if image_div:
            images = image_div.find_all('img')
            img_urls = [img.get('data-image') for img in images if img.get('data-image')]
        else:
            image_div = soup.find('div', class_='ProductItem-gallery-slides')
            if image_div:
                images = image_div.find_all('img')
                img_urls = [img.get('data-image') for img in images if img.get('data-image')]

        imgs_urls.append(img_urls)  # Append list of image URLs to images_list


        # description  <meta content='30" D x 29.5" H' itemprop="description"/>
        description_text = soup.find('meta', {'itemprop': 'description'})
        if description_text:
            description.append(
                clean_description(description_text.get('content')))
        else:
            description.append("")

        # Extract dimension text from meta tag
        dimension_meta = soup.find('meta', {'itemprop': 'description'})
        if dimension_meta:
            dimension_text = dimension_meta.get('content', '')  # Extract the content attribute
            extracted_width, extracted_height, extracted_depth = extract_core_dimensions(dimension_text)
            if extracted_width:
                width.append(extracted_width)
            else:
                width.append("")
            if extracted_height:
                height.append(extracted_height)
            else:
                height.append("")
            if extracted_depth:
                depth.append(extracted_depth)
            else:
                depth.append("")
        else:
            width.append("")
            height.append("")
            depth.append("")

        print(f"scraped : {url}")

   
else:
    print("No URLs to process.")

# print lengths of the lists
print(f"Length of title: {len(title)}")
print(f"Length of sku: {len(sku)}")
print(f"Length of price: {len(price)}")
print(f"Length of retail_price: {len(retail_price)}")
print(f"Length of description: {len(description)}")
print(f"Length of width: {len(width)}")
print(f"Length of height: {len(height)}")
print(f"Length of depth: {len(depth)}")
print(f"Length of images: {len(imgs_urls)}")



# # Create a dictionary with the data
df_data = {
    'title': title,
    'sku': sku,
    'price': price,
    'retail_price': retail_price,
    'description': description,
    'width': width,
    'height': height,
    'depth': depth,
    'images': imgs_urls,
}

# # Create a DataFrame
df = pd.DataFrame(df_data)
# save the data to a csv file
file_name = 'Rebound_Stores.csv'

full_path = directory_path + file_name
# Finally, write your DataFrame to a CSV file in the specified directory
df.to_csv(full_path, index=False, encoding='utf-8')
print(f"All data has been saved to {full_path}.")
