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
seat_height = []
quantity = []
brand_name = []
designer = []
imgs_urls = []
weight = []
tags = []

directory_path = "/Users/perobiora/Desktop/Kashew/Kashew_Python_Scrapers/Output/"
def normalize_dimension_text(dimension_text):
    # Normalize common variations in punctuation and spacing
    dimension_text = re.sub(r'[“”]', '"', dimension_text)  # Convert quotes
    dimension_text = re.sub(r'\s*x\s*', 'x', dimension_text)  # Normalize 'x' spacing
    dimension_text = dimension_text.replace('\n', ' ')  # Replace newlines with spaces
    return dimension_text

def extract_dimensions(dimension_text):
    dimension_text = normalize_dimension_text(dimension_text)

    patterns = [
        r'(\d+(?:\.\d+)?)"\s*W\s*x\s*(\d+(?:\.\d+)?)"\s*D\s*x\s*(\d+(?:\.\d+)?)"\s*H',  # '16.25" W x 22" D x 34" H'
        r'(\d+(?:\.\d+)?)"\s*H\s*x\s*(\d+(?:\.\d+)?)"\s*W\s*x\s*(\d+(?:\.\d+)?)"\s*D',  # '34" H x 16.25" W x 22" D'
        r'(\d+(?:\.\d+)?)"\s*D\s*x\s*(\d+(?:\.\d+)?)"\s*W\s*x\s*(\d+(?:\.\d+)?)"\s*H',  # '22" D x 16.25" W x 34" H'
        r'(\d+(?:\.\d+)?)"\s*W\s*(\d+(?:\.\d+)?)"\s*D\s*(\d+(?:\.\d+)?)"\s*H',  # '16.25" W 22" D 34" H'
        r'Width:\s*(\d+(?:\.\d+)?)["″]?\s*,\s*Depth:\s*(\d+(?:\.\d+)?)["″]?\s*,\s*Height:\s*(\d+(?:\.\d+)?)["″]?',  # 'Width: 16.25", Depth: 22", Height: 34"'
        r'(\d+(?:\.\d+)?)"\s*h\s*(\d+(?:\.\d+)?)"\s*w\s*(\d+(?:\.\d+)?)"\s*d',  # '34" h 16.25" w 22" d'
        r'(\d+(?:\.\d+)?)["″]?\s*(?:W|Width)',  # '16.25" W'
        r'(\d+(?:\.\d+)?)["″]?\s*(?:D|Depth)',  # '22" D'
        r'(\d+(?:\.\d+)?)["″]?\s*(?:H|Height)',  # '34" H'
        r'(\d+(?:\.\d+)?)"\s*Seat\s*Height',  # '18" Seat Height'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, dimension_text)
        if matches:
            # Extract dimensions with default values as "null" if not present
            dimensions = [match if match else "null" for match in matches[0]]
            # Adjust the dimensions length to always be three (W, H, D)
            while len(dimensions) < 3:
                dimensions.append("null")
            return dimensions[:3]  # Return the first three items (W, H, D)

    return "nothing", "nothing", "nothing"  # Return "nothing" if no dimensions are found


def clean_html(description_html):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(description_html, "html.parser")
    
    # Get text from parsed HTML, which automatically removes all HTML tags
    clean_text = soup.get_text(separator=' ')
    
    # Optional: Replace multiple spaces with a single space
    clean_text = ' '.join(clean_text.split())
    
    return clean_text

# Iterate over all the pages
it = 1 
while True and it < 5:
        response = session.get(
            f"https://www.modernresale.com/collections/2022-furniture?filter.v.availability=1&page={it}&sort_by=created-ascending", headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {it}: {response.status_code}")
            break
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all containers with the specified class
        product_outer = soup.find("div", class_="filters-adjacent collection-listing")

        product_container_inner = product_outer.find("div", class_="product-list product-list--per-row-5 product-list--per-row-mob-1 product-list--per-row-mob-1 product-list--image-shape-square")

        # find all <a with class product-link quickbuy-toggle
        products = soup.find_all("div", class_="product-info")

        for link in products:
            link = link.find("a", class_="product-link quickbuy-toggle")
            if link:
                 unique_urls.add(link.get("href"))

        print(f"Length of links: {len(unique_urls)}, Page: {it}")         
        it += 1

for url in list(unique_urls):
    complete_url = f"https://www.modernresale.com{url}"
    # complete_url = f"https://www.modernresale.com/products/emmemobili-boa-accent-chair?pr_prod_strat=e5_desc&pr_rec_id=ef3225db8&pr_rec_pid=8288694862110&pr_ref_pid=8141270581534&pr_seq=uniform"
    response = session.get(complete_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    # save the page to a file
    # with open("modern_resale.html", "w") as file:     
    #     file.write(soup.prettify())

    # TITLE
    title_text = soup.find("h1", class_="title").text
    if title_text:
        title.append(title_text)
    else:
         title.append("")

    # Find the script tag with specific id and type
    script_tag = soup.find('script', id='WH-ProductJson-product-template', type='application/json')

    if script_tag:
        json_data = json.loads(script_tag.string)
        # Extract ID from JSON data
        product_id = json_data.get('id', '')
        if product_id:
            sku.append(product_id)
        else:
            sku.append("")

        # Extract price from JSON data and convert from cents to dollars
        product_price = json_data.get('price', 0) / 100
        extracted_price = int(product_price)
        if extracted_price:
            current_price.append(product_price)
        else:
            current_price.append("")

        
        # extract compare_at_price from JSON data and convert from cents to dollars
        compare_at_price = json_data.get('compare_at_price', 0)
        if compare_at_price is None:
            compare_at_price = 0  # Set to 0 if None
        extracted_compare_at_price = int(compare_at_price / 100)

        if extracted_compare_at_price != 0:
            previous_price.append(extracted_compare_at_price)
        else:
            previous_price.append("")

        # Extract inventory_quantity from the first variant as an example
        if 'variants' in json_data and json_data['variants']:
            first_variant_quantity = json_data['variants'][0].get('inventory_quantity', 0)
            quantity.append(first_variant_quantity)
        else:
            quantity.append("")
            print("No variants found or inventory_quantity not available")

        # brand 
        brand = json_data.get('vendor', '')
        if brand:
            brand_name.append(brand)
        else:
            brand_name.append("")

        # description
        description_text = json_data.get('content', '') 
        if description_text:
            clean_description = clean_html(description_text)
            description.append(clean_description)
        else:
            description.append("")

        # script tag for other
        script_tag_2 = soup.find('script', id=f"ProductJson-{product_id}", type='application/json') 

        if script_tag_2:
            try:
                json_data_2 = json.loads(script_tag.string)

                # Extract weight from the first variant
                weight_in_hundredths = json_data_2['variants'][0].get('weight', 0)
                extracted_weight = weight_in_hundredths / 1000  # Convert to pounds

                # Print extracted weight
                weight.append(extracted_weight)

                # images
                images = json_data_2.get('images', [])
                # images have two // at the beginning, so we need to add https: to the beginning
                if images:
                    imgs_urls.append(['https:' + img for img in images])
                else:
                    imgs_urls.append("")

                # tags
                product_tags = json_data_2.get('tags', [])
                if product_tags:
                    tags.append(product_tags)
                else:
                    tags.append("")

            except json.JSONDecodeError:
                print("Error decoding JSON data.")
                weight.append("")


    else:
        print("Script tag not found or invalid structure.")

    # Extracting dimensions from the second section of the product description, if available
    accordion_sections = soup.find_all('div', class_='product-detail-accordion')
    if len(accordion_sections) > 1:  # Check if there is at least a second section
        second_section = accordion_sections[1]  # Access the second section
        dimension_text_spans = second_section.find_all('span', class_='metafield-multi_line_text_field')
        for dimension_text_span in dimension_text_spans:
            if dimension_text_span:
                dimension_text = dimension_text_span.text.strip()
                w, h, d = extract_dimensions(dimension_text)
                if w != "nothing":
                    width.append(w)
                else:
                    width.append("")  # Append empty string if nothing was found
                if h != "nothing":
                    height.append(h)
                else:
                    height.append("")  # Append empty string if nothing was found
                if d != "nothing":
                    depth.append(d)
                else:
                    depth.append("")  # Append empty string if nothing was found
    else:
        print("Second section not available.")
        # Optionally append empty strings to maintain list lengths
        width.append("")
        height.append("")
        depth.append("")

    print(f"Processed {url}.")
 

# print lenth 
print(f"Title: {len(title)}, SKU: {len(sku)}, Current Price: {len(current_price)}, Previous Price: {len(previous_price)}, Brand: {len(brand_name)}, Description: {len(description)}, Width: {len(width)}, Height: {len(height)}, Depth: {len(depth)}, Images: {len(imgs_urls)}, Weight: {len(weight)}")


# Create a DataFrame from the extracted data
df = pd.DataFrame({
    'title': title,
    'sku': sku,
    'price': current_price,
    'retail_price': previous_price,
    'brand': brand_name,
    'description': description,
    'width': width,
    'height': height,
    'depth': depth,
    'images': imgs_urls,
    'weight': weight,
    'tags': tags,
    'quantity': quantity,
})

# remove rows with quantity less than 1
df = df[df['quantity'] > 0]


# Save the DataFrame to a CSV file
output_file = os.path.join(directory_path, "modern_resale.csv")
df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
