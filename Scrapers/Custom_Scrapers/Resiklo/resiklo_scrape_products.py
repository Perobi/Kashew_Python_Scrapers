import time
import requests
from bs4 import BeautifulSoup
import csv
import json
import re
import csv



def extract_core_dimensions(dimension_text):
    dimensions = {'width': None, 'depth': None, 'height': None}

    # Handle dimensions given as "48x48x18" or with additional details
    compact_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)(?:;|$)', re.IGNORECASE)

    # Existing patterns for comparison
    dia_h_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*”?\s*Dia\s*x\s*(\d+(?:\.\d+)?)\s*”?\s*H', re.IGNORECASE)
    general_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*”?\s*[LWD](?:\s*x\s*(\d+(?:\.\d+)?)\s*”?\s*[LWDH](?:\s*x\s*(\d+(?:\.\d+)?)\s*”?\s*H)?)?', re.IGNORECASE)

    # First, check for compact pattern
    compact_match = compact_pattern.search(dimension_text)
    if compact_match:
        dimensions['width'], dimensions['depth'], dimensions['height'] = compact_match.groups()
    else:
        # Check for diameter and height
        dia_h_match = dia_h_pattern.search(dimension_text)
        if dia_h_match:
            dimensions['width'] = dimensions['depth'] = dia_h_match.group(1)
            dimensions['height'] = dia_h_match.group(2)
        else:
            # General pattern matching
            general_match = general_pattern.search(dimension_text)
            if general_match:
                dimension_values = general_match.groups()
                if dimension_values[0]:
                    dimensions['width'] = dimension_values[0]
                if dimension_values[1]:
                    dimensions['depth'] = dimension_values[1]
                if dimension_values[2]:  # Height is present
                    dimensions['height'] = dimension_values[2]

    return dimensions

def make_request_with_retry(url, max_attempts=5, delay=5):
    """
    Attempts to make a request up to max_attempts times with a delay between each attempt.
    """
    for attempt in range(max_attempts):
        time.sleep(1)  # Add a short delay before each attempt
        response = requests.get(url)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            print(f"Rate limit exceeded. Waiting {delay} seconds before retrying...")
            time.sleep(delay)
            # Optionally increase delay here to back off more in subsequent attempts
        else:
            # Handle other types of errors (e.g., 404 or 500) as needed
            print(f"Failed to retrieve item at {url}. Status code: {response.status_code}")
            return None
    print(f"Failed to retrieve item after {max_attempts} attempts: {url}")
    return None


# Base URL for constructing full item URLs
base_url = 'https://resiklodesign.com'
# Fetch the initial JSON data
url = 'https://tools.squarewebsites.org/sqs-response/resiklodesign-com/page-context/shop.js?ver=2024-03-29T16-5'
response = requests.get(url)
data = response.json() if response.status_code == 200 else {}

items = data.get('items', [])

# Prepare a list to hold all item data
all_items_data = []

for item in items:
    item_data = {
        'title': None,
        'sku': None,
        'price': None,
        'retail_price': None,
        'description': None,
        'width': None,
        'depth': None,
        'height': None,
        'tags': [],
        'images': [],
        'quantity': None,
    }
    
    full_url = base_url + item.get('fullUrl', '')
    item_response = make_request_with_retry(full_url)
    if item_response is not None:

        if item_response.status_code == 200:
            soup = BeautifulSoup(item_response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find("h1", {"class": "ProductItem-details-title"})
            if title_tag:
                item_data['title'] = title_tag.get_text(strip=True)
            
            # Extract SKU, price, and more from JSON embedded in script tag
            script_tag = soup.find('script', string=re.compile('Static.SQUARESPACE_CONTEXT'))
            if script_tag:
                script_content = script_tag.string
                json_object_match = re.search(r'Static.SQUARESPACE_CONTEXT = ({.*?});', script_content, re.DOTALL)
                if json_object_match:
                    json_str = json_object_match.group(1)
                    json_data = json.loads(json_str)
                    variant = json_data["product"]["variants"][0]
                    item_data['sku'] = variant["sku"]
                    item_data['price'] = variant["salePrice"]["value"] / 100
                    item_data['retail_price'] = variant["price"]["value"] / 100
                    # "stock":{"unlimited":false,"quantity":1}
                    item_data['quantity'] = variant.get("stock", {}).get("quantity")
            # Extract description
            description_div = soup.find("div", {"class": "ProductItem-details-excerpt"})
            if description_div:
                item_data['description'] = description_div.get_text(strip=True)
            
            # Extract dimensions
            dimension_text = soup.find(text=re.compile(r'Dimensions:'))
            if dimension_text:
                dimensions = extract_core_dimensions(dimension_text)
                if dimensions:
                    item_data.update(dimensions)
            
            # Extract tags
            article = soup.find('article', class_='ProductItem')
            if article:
                classes = article.get('class', [])
                for class_name in classes:
                    if class_name.startswith('tag-'):
                        item_data['tags'].append(class_name[len('tag-'):])
            
            # Extract image URLs
            image_elements = soup.find_all("img", {"class": "ProductItem-gallery-thumbnails-item-image"})
            for img in image_elements:
                image_url = img.get('data-src')
                if image_url:
                    item_data['images'].append(image_url)
            
            all_items_data.append(item_data)
            print(f"Processed item: {item_data['title']}")
            print( 
                str(len(all_items_data)) + "of" + str(len(items)) + " items processed")
            print ("title : " + item_data['title'])
        else:
            # Handling non-200 responses for each item
            print(f"Failed to retrieve item at {full_url}. Status code: {item_response.status_code}")  
    else:
        print(f"Failed to retrieve item at {full_url}. No response received")
        # Optionally handle the case where no response is received for an item          
# Writing data to CSV

directory_path = "/Users/perobiora/Desktop/Kashew/Kashew_Python_Scrapers/Output/"
csv_file = "Resiklo_CSV.csv"
full_path = directory_path + csv_file  # Concatenate to get the full file path

csv_columns = ['title', 'sku', 'quantity', 'price', 'retail_price', 'description', 'width', 'depth', 'height', 'tags', 'images']

try:
    with open(full_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in all_items_data:  # Ensure all_items_data is defined and populated with your data dictionaries
            # Convert lists to strings for CSV output
            if 'tags' in data and isinstance(data['tags'], list):
                data['tags'] = ', '.join(data['tags'])
            if 'images' in data and isinstance(data['images'], list):
                data['images'] = ', '.join(data['images'])
            writer.writerow(data)
except IOError:
    print("I/O error")
