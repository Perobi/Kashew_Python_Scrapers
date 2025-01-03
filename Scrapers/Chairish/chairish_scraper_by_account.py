import json
import subprocess
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
    from urllib.parse import urlparse
    from bs4 import BeautifulSoup

directory_path = "/Users/perobiora/Desktop/Kashew/Kashew_Python_Scrapers/Output/"
# profiles = ["4kqk0w", "maisonlobo", "rusticodecor", "eclecticcollective", "designplus", "ata"]

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}


for profile in profiles:
    title = []
    sku_list = []
    current_price = []
    previous_price = []
    main_category = []
    sub_category = []
    description = []
    width = []
    height = []
    depth = []
    location = []
    brand_name = []
    imgs_urls = []
    it = 1
    
    while True:
        response = session.get(
            f"https://www.chairish.com/shop/{profile}?page_size=96&page={it}", headers=headers)
        if response.status_code != 200:
            print(response.status_code)
            break
        soup = BeautifulSoup(response.text, "html.parser")
        urls = soup.select(
            "div.product-grid-container > div > div > div > div > a")
        print(f"page {it} : {len(urls)}")
        it += 1
        for url in urls:
            url = url["href"]
            response2 = session.get(url, headers=headers)
            soup2 = BeautifulSoup(response2.text, "html.parser")
            scripts = soup2.select("body > script:nth-child(2)")
            if not scripts:  # Check if the list is empty
                print(f"No script tag found at URL: {url}. Skipping...")
                continue  # Skip the rest of the code in this loop iteration and continue with the next URL
            
            # with open('response.html', 'w', encoding='utf-8') as file:
            #     file.write(response2.text)

            script = scripts[0].string.strip()
            data = json.loads(script)
            # Extracting SKU from URL
            try:
                sku = url.split("/product/")[1].split("/")[0]  # The SKU is the number after "/product/"
            except IndexError:
                print(f"Couldn't extract SKU from URL: {url}")
                sku = ""
            sku_list.append(sku)

            try: 
                description.append(data['description'])
            except: 
                description.append("")
                print("No description for this item")
            try: 
                width.append(int(data['width']['value']))
            except:
                width.append("")
                print("No width for this item")
            try:
                height.append(int(data['height']['value']))
            except:
                height.append("")
                print("No height for this item")
            try:
                depth.append(int(data['depth']['value']))
            except:
                depth.append("")
                print("No depth for this item")

            title.append(data['name'])

            current_price.append(data['offers']["price"])
            try:
                brand_name.append(data['brand']["name"])
            except:
                brand_name.append("")
            try:
                p_price = soup2.select(
                    ".product-price-wrapper .product-price-previous span.product-price-value")[0].text.replace("$", "")
                previous_price.append(p_price)
            except:
                previous_price.append("")

            categories = soup2.select(
                "div.quick-buttons.js-quick-buttons > div")[0]['data-taxonomy'].split("/")
            category = categories[0]
            main_category.append(category)

            location_element = soup2.select_one("span.js-product-ships-from")
            if location_element:
                loc_text = location_element.get_text(strip=True)
                # Extracting text after "from".
                from_index = loc_text.find("from")
                if from_index != -1:  # Making sure "from" is in the string
                    loc = loc_text[from_index + len("from "):]  # Slice the string from "from " onwards
                    location.append(loc)
                    print(f"Location: {loc}")
                else:
                    location.append("")  # In case there's no "from" in the string, which is unexpected
                    print(f"Unexpected location format: {loc_text}. URL: {url}")
            else:
                location.append("")
                print(f"No location for this item. URL: {url}")  # Print the URL for manual inspection

            try:
                s_category = categories[1]
                sub_category.append(s_category)
            except IndexError:
                sub_category.append("")
            urls_img = soup2.select("ul > li > img")
            imgs_url = []
            for url_i in urls_img:
                img_url = urlparse(url_i['src'])
                url_i = url_i['src'].replace(img_url.query, "")[:-1]
                imgs_url.append(url_i)
            imgs_urls.append(imgs_url)
            print(f"Scraped -- {data['name']}")

    df_data = {
        "sku": sku_list,
        "title": title,
        "description": description,
        "price": current_price,
        "retail_price": previous_price,
        "images": imgs_urls,
        "category": main_category,
        "sub_category": sub_category,
        "brand": brand_name,
        "width": width,
        "height": height,
        "depth": depth,
        "location": location
    }

    df = pd.DataFrame(df_data)

    file_name = f"{profile}.csv"
    full_path = directory_path + file_name
    df.to_csv(full_path, index=False, encoding='utf-8')
    print("finished scraping profile: ", profile)

print("Done!")
