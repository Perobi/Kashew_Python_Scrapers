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

processed_count = 0

# Urls
categories = ["seating","storage", "tables", "lighting", "accessories"]
unique_urls = set()  # This set will store unique URLs for all categories


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
title = []
sku = []
current_price = []
previous_price = []
main_category = []
sub_category = []
description = []
width = []
height = []
depth = []
tags = []
brand_name = []
designer = []
imgs_urls = []

directory_path = "/Users/perobiora/Desktop/Kashew_Python_Scrapers/Output/"

for category in categories:
    print(f"Starting category: {category}")
    it = 1  # Reset the iterator for each category
    while True:
        response = session.get(
            f"https://midcenturymobler.com/collections/{category}?page={it}", headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {it} for category {category}: {response.status_code}")
            break
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all containers with the specified class
        product_containers = soup.find_all("div", class_="boost-pfs-container-default-fullwidth")

        # Check if there are at least five such containers
        if len(product_containers) >= 5:
            # Select the fifth container that holds the products
            product_holder = product_containers[4]  # Indexing starts from 0, so 4 is the fifth item

            # Within the product holder, find all the 'a' tags
            product_links = product_holder.find_all("a")
            if not product_links:  # Check if there are no product links
                print(f"No more products found on page {it} for category {category}. Moving to next category.")
                break

            for link in product_links:
                product_url = link.get("href")
                if product_url:
                    # Remove URL fragment (anything after a #)
                    product_url = product_url.split('#')[0]
                    if not product_url.startswith('http'):
                        product_url = f"https://midcenturymobler.com{product_url}"
                    unique_urls.add(product_url)  # Add the URL to the set to keep track of uniqueness
                    print(f"Product URL: {product_url}")
        else:
            print(f"Not enough product containers found on page {it} for category {category}. Moving to next category.")
            break

        it += 1
        



     
for url in unique_urls:
    product_tags = []
    product_imgs_urls = []
    print(url)  # Print the URL

    response2 = session.get(url, headers=headers)
    soup2 = BeautifulSoup(response2.text, "html.parser")
    scripts = soup2.find('script', {'type': 'application/json', 'data-rvpproduct-json': True})
    if not scripts:  
        print(f"No script tag found at URL: {url}. Skipping...")
        break

    script = scripts.string.strip()  
    data = json.loads(script)
    # Title
    title_text = data.get('title', '').lower().title()

    title.append(title_text)


    # SKU (assuming it's the same as the 'handle')
    sku.append(data.get('id', ''))

    # Current price (divided by 100 if price is in cents)
    current_price.append(data.get('price', 0) / 100)

    # Previous price (divided by 100 if price is in cents)
    previous_price_value = data.get('compare_at_price', None)
    if previous_price_value is not None:
        previous_price.append(previous_price_value / 100)
    else:
        previous_price.append("")
        
        
    url_parts = url.split('/')
    main_category_segment_index = url_parts.index('collections') + 1
    if main_category_segment_index < len(url_parts):
        main_category_value = url_parts[main_category_segment_index]
    else:
        main_category_value = ""

    # Append the extracted data to the lists
    main_category.append(main_category_value)
    sub_category.append(data.get('type', ""))   # Placeholder


        # description
    description_text = data.get('description', '')

    # Check if description_text is not empty
    if description_text:
        # Replace <br> tags with a period and a space
        description_text_with_periods = re.sub(r'<br\s*/?>', '. ', description_text)
        # Remove any remaining HTML tags
        cleaned_description = re.sub(r'<[^<]+?>', '', description_text_with_periods)

        # Remove extra spaces and periods that might have been added, e.g., ".." or " ."
        cleaned_description = re.sub(r'\.\s*\.', '.', cleaned_description)  # Adjusted to remove multiple periods to a single one.
        cleaned_description = re.sub(r'\s+\.', '.', cleaned_description)  # Remove spaces before period
        # Trim leading/trailing whitespace and ensure there's only one space between sentences
        cleaned_description = ' '.join(cleaned_description.split())

        # Append to description list
        description.append(cleaned_description)
    else:
        # If description_text is empty, append an empty string or a placeholder
        description.append('')


    # Regular expressions to match the dimensions directly from the description
    width_pattern = r'(\d+(?:\.\d+)?)["″]? wide'
    height_pattern = r'(\d+(?:\.\d+)?)["″]? tall'
    depth_pattern = r'(\d+(?:\.\d+)?)["″]? deep'

    width_match = re.search(width_pattern, cleaned_description)
    height_match = re.search(height_pattern, cleaned_description)
    depth_match = re.search(depth_pattern, cleaned_description)

    # If not found in the description, try matching from the tags list
    if not width_match:
        for tag in data.get('tags', []):
            if 'width:' in tag.strip().lower():
                width_match = re.search(r'width:\s*(\d+(?:\.\d+)?)', tag, re.IGNORECASE)

    if not height_match:
        for tag in data.get('tags', []):
            if 'height:' in tag.strip().lower():
                height_match = re.search(r'height:\s*(\d+(?:\.\d+)?)', tag, re.IGNORECASE)

    if not depth_match:
        for tag in data.get('tags', []):
            if 'depth:' in tag.strip().lower():
                depth_match = re.search(r'depth:\s*(\d+(?:\.\d+)?)', tag, re.IGNORECASE)

    # Extracting the width, height, and depth if available
    width.append(width_match.group(1) if width_match else "")
    height.append(height_match.group(1) if height_match else "")
    depth.append(depth_match.group(1) if depth_match else "")


     # Regular expression to match the manufacturer
    manufacturer_match = re.search(r'Manufacturer:\s*(.*?)<br>', description_text)
    # Check if the manufacturer is not 'Unknown'
    if manufacturer_match:
        manufacturer_text = html.unescape(manufacturer_match.group(1))  # Decode HTML entities
        manufacturer_text = BeautifulSoup(manufacturer_text, 'html.parser').get_text()
        if manufacturer_text.strip().lower() != "unknown":
            manufacturer = manufacturer_text.strip()
        else:
            manufacturer = ""
    else:
        manufacturer = ""
    brand_name.append(manufacturer)

    # Regular expression to match the designer
    designer_match = re.search(r'Designer:\s*(.*?)<br>', description_text)
    # Check if the designer is not 'Unknown'
    if designer_match:
        designer_text = html.unescape(designer_match.group(1))  # Decode HTML entities
        designer_text = BeautifulSoup(designer_text, 'html.parser').get_text()
        if designer_text.strip().lower() != "unknown":
            designerName = designer_text.strip()
        else:
            designerName = ""
    else:
        designerName = ""
    designer.append(designerName)


    # Extracting tags and image URLs
    product_tags.extend(data.get('tags', []))
    product_imgs_urls.extend(['https:' + img for img in data.get('images', []) if img.startswith('//')])
    tags.append(', '.join(product_tags))  # Join tags with a semicolon
    imgs_urls.append(', '.join(product_imgs_urls))  # Join image URLs with a semicolon
    # processed_count += 1


print(f"Lengths - title: {len(title)}, sku: {len(sku)}, current_price: {len(current_price)}, previous_price: {len(previous_price)}, main_category: {len(main_category)}, sub_category: {len(sub_category)}, description: {len(description)}, width: {len(width)}, height: {len(height)}, depth: {len(depth)}, tags: {len(tags)}, brand_name: {len(brand_name)}, imgs_urls: {len(imgs_urls)}")


df_data = {
    'title': title,
    'sku': sku,
    'price': current_price,
    'retail_price': previous_price,
    'category': main_category,
    'sub_category': sub_category,
    'description': description,
    'width': width,
    'height': height,
    'depth': depth,
    'tags': tags,
    'brand': brand_name,
    'designer': designer,
    'images': imgs_urls
}

# Create a DataFrame
df = pd.DataFrame(df_data)

file_name = 'Mid_Century_Mobler.csv'

full_path = directory_path + file_name

# Define the path for the new CSV file, use os.getcwd() to get the current working directory


# Finally, write your DataFrame to a CSV file in the specified directory
df.to_csv(full_path, index=False, encoding='utf-8')

print(f"All data has been saved to {full_path}.")