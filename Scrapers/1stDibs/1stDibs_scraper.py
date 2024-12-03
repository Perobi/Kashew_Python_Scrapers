import json
import subprocess
try:
    import pandas as pd
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from urllib.parse import urlparse, urlunparse, parse_qs
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
    from urllib.parse import urlparse
    from bs4 import BeautifulSoup

import time


directory_path = "/Users/perobiora/Desktop/Kashew/Kashew_Python_Scrapers/Output/"
profiles = ["abend-gallery"]

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}


# Function to add delay between requests (throttling)
def slow_request(delay=0.5):
    time.sleep(delay)

# Function to handle retries for failed requests
def get_with_retries(url, headers, retries=5, delay=1):
    attempt = 0
    while attempt < retries:
        print(f"Fetching...Attempt {attempt + 1}")
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            else:
                print(f"Request failed with status code {response.status_code}, retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Request failed due to error: {e}, retrying...")
        
        attempt += 1
        slow_request(delay)  # Use the slow_request function for throttling
    
    print(f"Failed to retrieve {url} after {retries} attempts.")
    return None



for profile in profiles:
    title = []
    sku_list = []
    current_price = []
    previous_price = []
    description = []
    material = []
    width = []
    height = []
    depth = []
    style = []
    brand_name = []
    imgs_urls = []
    tags = []
    seat_height = []
    it = 1

    while it < 2:
        # Fetch the page content
        response = get_with_retries(
            f"https://www.1stdibs.com/dealers/{profile}/shop/?page={it}&sort=newest",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Failed to fetch page {it}, status code: {response.status_code}")
            break

        # Check if the current URL in the response is the same as the base URL (indicating a redirect to the main shop page)
        if response.url == f"https://www.1stdibs.com/dealers/{profile}/shop/":
            print(f"Redirected to main shop page. Page {it} does not exist. Stopping the loop.")
            break
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract all item URLs
        links = soup.select('div[data-tn="search-results-container"] a[data-tn="item-tile-title-anchor"]')
        # Extract href attributes
        urls = [link['href'] for link in links if 'href' in link.attrs]
        # Check if any URLs were found
        if not urls:
            print("No more items found on page", it)
            break
        # Print or process the extracted URLs
        print(f"Page {it} URLs:")
        print(len(urls))
        
        it += 1

        for url in urls:
            full_url = f"https://www.1stdibs.com/{url}"
            response2 = get_with_retries(full_url, headers)
            if not response2:
                continue  # Skip to the next URL if the request failed

            soup2 = BeautifulSoup(response2.text, "html.parser")
            #Extract title
            try:
                title_tag = soup2.find("span", {"class": "_4a80dd6a", "data-tn": "pdp-item-title"})
                title_text = title_tag.get_text(strip=True) if title_tag else ""
                title.append(title_text)
            except Exception as e:
                title = f"Error extracting title: {e}"
                title.append("")

            # Extract description
            try:
                description_tag = soup2.find("span", {"class": "_dda3618c", "data-tn": "pdp-item-description-content"})
                description_text = description_tag.get_text(strip=True) if description_tag else "Description not found"
                description.append(description_text)
            except Exception as e:
                description = f"Error extracting description: {e}"
                description.append("")


            #  SKU 
            try:
                sku_num = url.split("id-a_")[1].split("/")[0] 
                sku_list.append(sku_num)
            except IndexError:
                print("Error extracting SKU from the URL.")
                sku_list.append("")

            # Price extraction and appending to current_price
            script_tag = soup2.find("script", {"type": "application/ld+json"})
            if script_tag:
                try:
                    # Load the JSON content
                    json_data = json.loads(script_tag.string)
                    
                    # Look for the product object and extract the price
                    product_data = next((item for item in json_data if item["@type"] == "Product"), None)
                    if product_data and "offers" in product_data:
                        price = product_data["offers"].get("price", "")
                        current_price.append(price)  # Append the extracted price
                    else:
                        print("Product or price information not found.")
                        current_price.append("")  # Append default value if not found
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    current_price.append("")  # Append error placeholder
            else:
                print("JSON-LD <script> tag not found.")
                current_price.append("")  # Append placeholder if script tag not found

            # Dimensions extraction and appending to width, height, depth
            try:
                dimensions_div = soup2.find("div", {"data-tn": "pdp-spec-dimensions"})
                
                # Extract Height
                height_span = dimensions_div.find("span", {"data-tn": "pdp-spec-detail-height"})
                if height_span:
                    height_text = height_span.get_text(strip=True)
                    height_value = float(height_text.split(" in")[0].split(":")[1].strip())
                else:
                    height_value = 1  # Default if not found
                height.append(height_value)

                # Extract Width
                width_span = dimensions_div.find("span", {"data-tn": "pdp-spec-detail-width"})
                if width_span:
                    width_text = width_span.get_text(strip=True)
                    width_value = float(width_text.split(" in")[0].split(":")[1].strip())
                else:
                    width_value = 1  # Default if not found
                width.append(width_value)

                # Extract Depth
                depth_span = dimensions_div.find("span", {"data-tn": "pdp-spec-detail-depth"})  # Assuming similar structure for depth
                if depth_span:
                    depth_text = depth_span.get_text(strip=True)
                    depth_value = float(depth_text.split(" in")[0].split(":")[1].strip())
                else:
                    depth_value = 1  # Default if not found
                depth.append(depth_value)

                # extract_seat_height
                seat_height_span = dimensions_div.find("span", {"data-tn": "pdp-spec-detail-secondaryHeight"})
                if seat_height_span:
                    seat_height_text = seat_height_span.get_text(strip=True)
                    seat_height_value = float(seat_height_text.split(" in")[0].split(":")[1].strip())
                else:
                    seat_height_value = ""
                seat_height.append(seat_height_value)
            

                # Print extracted values for debugging

            except Exception as e:
                print(f"Error extracting dimensions: {e}")
                # Append defaults if any exception occurs
                height.append(1)
                width.append(1)
                depth.append(1)

            # Brand extraction and appending to brand_name
            try:
                brand_tag = soup2.find("span", {"data-tn": "pdp-spec-detail-creator"})
                brand_text = brand_tag.get_text(strip=True) if brand_tag else ""
                brand_name.append(brand_text)
            except Exception as e:
                print(f"Error extracting brand: {e}")
                brand_name.append("")
    
            # Material extraction and appending to material list
            materials_list = []
            try:
                materials_div = soup2.find("div", {"data-tn": "pdp-spec-medium"})
                if materials_div:
                    # Find all material spans or links within the container
                    material_links = materials_div.find_all("a", {"class": "_1862016c _57a9be25"})
                    materials = [link.get_text(strip=True) for link in material_links]
                else:
                    materials = [""]
                materials_list.append(", ".join(materials))  # Append materials as a comma-separated string
            except Exception as e:
                print(f"Error extracting materials from 'pdp-spec-medium': {e}")
                materials_list.append("")  # Append default in case of error

            # More materials
            try:
                materials_div = soup2.find("span", {"data-tn": "pdp-spec-materials-and-techniques"})
                if materials_div:
                    # Find all material spans or links within the container
                    material_links = materials_div.find_all("a", {"class": "_1862016c _57a9be25"})
                    materials = [link.get_text(strip=True) for link in material_links]
                else:
                    materials = [""]
                materials_list.append(", ".join(materials))  # Append materials as a comma-separated string
            except Exception as e:
                print(f"Error extracting materials from 'pdp-spec-materials-and-techniques': {e}")
                materials_list.append("")  # Append default in case of error

            material.append(", ".join(materials_list))    

            # Style extraction and appending to style list
            try:
                style_div = soup2.find("span", {"data-tn": "pdp-spec-detail-style"})
                if style_div:
                    # Extract the style link
                    style_link = style_div.find("a", {"class": "_1862016c _57a9be25"})
                    if style_link:
                        style_text = style_link.get_text(strip=True)
                    else:
                        style_text = ""
                else:
                    style_text = ""  # Default if not found
                style.append(style_text)  # Append style

                # Print extracted style for debugging

            except Exception as e:
                print(f"Error extracting style: {e}")
                style.append("")  # Append default in case of error

            # Extract the date of manufacture and append to tags
            tag_list = []
            try:
                date_of_manufacture_tag = soup2.find("span", {"data-tn": "pdp-spec-detail-dateOfManufacture"})
                if date_of_manufacture_tag:
                    date_of_manufacture_text = date_of_manufacture_tag.get_text(strip=True)
                    tag_list.append(f"Created in {date_of_manufacture_text}")  # Append the formatted date
            except Exception as e:
                print(f"Error extracting date of manufacture: {e}")
                tag_list.append("")  # Append default in case of error

            # Extract the period and append to tags
            try:
                period_tag = soup2.find("span", {"data-tn": "pdp-spec-detail-period"})
                if period_tag:
                    period_link = period_tag.find("a", {"class": "_1862016c _57a9be25"})
                    if period_link:
                        period_text = period_link.get_text(strip=True)
                        tag_list.append(f"Period: {period_text}")  # Append the period text
            except Exception as e:
                print(f"Error extracting period: {e}")
                tag_list.append("")  # Append default in case of error


           #country of origin
            try:
                origin_tag = soup2.find("span", {"data-tn": "pdp-spec-detail-origin"})
                if origin_tag:
                    origin_link = origin_tag.find("a", {"class": "_1862016c _57a9be25"})
                    if origin_link:
                        origin_text = origin_link.get_text(strip=True)
                        tag_list.append(f"Place of Origin: {origin_text}")  # Append the period text
            except Exception as e:
                print(f"Error extracting period: {e}")
                tag_list.append("")  # Append default in case of error

            tags.append(
                # join the tag list with a comma and space
                ", ".join(tag_list)
            )  # Append tags as a comma-separated string

            # Image extraction from buttons containing <noscript> tags
            image_buttons = soup2.find_all("button", {"data-tn": True})
            img_list = []
            for button in image_buttons:
                # Check if the button contains a <noscript> tag
                noscript_tag = button.find("noscript")
                if noscript_tag:
                    img_tag = noscript_tag.find("img")
                    if img_tag and 'src' in img_tag.attrs:
                        img_url = img_tag.attrs['src']
                        # Clean the image URL by removing query parameters
                        parsed_url = urlparse(img_url)
                        clean_url = urlunparse(parsed_url._replace(query=''))
                        img_list.append(clean_url)
                
                # Check for img tags directly within the button (for non-lazy-loaded images)
                img_tag = button.find("img")
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag.attrs['src']
                    # Clean the image URL by removing query parameters
                    parsed_url = urlparse(img_url)
                    clean_url = urlunparse(parsed_url._replace(query=''))
                    img_list.append(clean_url)

                    # remove duplicates
            img_list = list(set(img_list))

            imgs_urls.append(
                # join 
                ", ".join(img_list)
            )
            previous_price.append("")


    print("Length of title: ", len(title), 
           "Length of current_price: ", len(current_price), 
           "Length of previous_price: ", len(previous_price), 
           "Length of description: ", len(description), 
           "Length of material: ", len(material), 
           "Length of width: ", len(width), 
           "Length of height: ", len(height), 
           "Length of depth: ", len(depth), 
           "Length of style: ", len(style), 
           "Length of brand_name: ", len(brand_name), 
           "Length of imgs_urls: ", len(imgs_urls), 
           "Length of tags: ", len(tags), 
           "Length of seat_height: ", len(seat_height),)

    df_data = {
        "sku": sku_list,
        "title": title,
        "description": description,
        "price": current_price,
        "retail_price": previous_price,
        "images": imgs_urls,
        "brand": brand_name,
        "width": width,
        "height": height,
        "seat_height": seat_height,
        "depth": depth,
        "material": material,
        "style": style,
        "tags": tags

    }

    df = pd.DataFrame(df_data)

    file_name = f"{profile}.csv"
    full_path = directory_path + file_name
    df.to_csv(full_path, index=False, encoding='utf-8')
    print("finished scraping profile: ", profile)

print("Done!")
