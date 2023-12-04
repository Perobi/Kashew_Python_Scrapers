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
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}



# Changeable variables
link = "https://www.chairish.com/pros"
located = "Los+Angeles"


links= []


it = 1
while True:
    response = session.get(
        f"https://www.chairish.com/pros?location={located}&page_size=96&page={it}", headers=headers)
    if response.status_code != 200:
        print(response.status_code)
        break
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all <a> elements within the <li> elements and add them to the links list
    lis = soup.select("li > a.card-business.js-business")
    for li in lis:
        href = li.get("href")
        if href:
            links.append(href)

    print(f"page {it} : {len(lis)}")
    print(links)
    it += 1  

name = []
website = []
instagram = []
facebook = []
pinterest = []
twitter = []
location = []
profession = []
chairish_profile = []


# Create a set to keep track of sellers already processed
processed_sellers = set()

for link in links:
    response2 = session.get(f"https://www.chairish.com{link}", headers=headers)
    if response2.status_code != 200:
        print(response2.status_code)
        continue

    soup2 = BeautifulSoup(response2.text, "html.parser")

    # Extracting location and profession (only the first occurrence)
    location_elem = soup2.select_one("ul.shop-meta-list > li > a")
    profession_elem = soup2.select_one("ul.shop-meta-list > li:nth-of-type(2)")

    if location_elem:
        location_text = location_elem.get_text(strip=True)
    else:
        location_text = None

    if profession_elem:
        profession_text = profession_elem.get_text(strip=True)
    else:
        profession_text = None

    # Extracting website and Instagram links
    social_media_links = soup2.select("ul.js-social-media-links > li > a")
    website_link = None
    instagram_link = None
    facebook_link = None
    pinterest_link = None
    twitter_link = None


    for link_elem in social_media_links:
        href = link_elem.get("href")
        if "instagram.com" in href:
            instagram_link = href
        elif "facebook.com" in href:
            facebook_link = href
        elif "pinterest.com" in href:
            pinterest_link = href
        elif "twitter.com" in href:
            twitter_link = href    
        elif "http" in href:
            website_link = href

    # Extracting name from the link
    name_elem = link.split("/")[-1]

    # Check if this seller has already been processed
    if name_elem in processed_sellers:
        continue

    # Add the seller to the set of processed sellers
    processed_sellers.add(name_elem)

    # Add data to lists
    name.append(name_elem)
    website.append(website_link)
    instagram.append(instagram_link)
    location.append(location_text)
    profession.append(profession_text)
    chairish_profile.append(link)
    twitter.append(twitter_link)
    facebook.append(facebook_link)
    pinterest.append(pinterest_link)

# Create the DataFrame and save to CSV
df = pd.DataFrame({ 
    "name": name,
    "website": website,
    "instagram": instagram,
    "location": location,
    "profession": profession,
    "chairish_profile": chairish_profile,
    "twitter": twitter,
    "facebook": facebook,
    "pinterest": pinterest
})

file_name = f"{located}.csv"
directory_path = "/Users/perobiora/Desktop/Kashew/PythonScraper/Output/"

full_path = directory_path + file_name
df.to_csv(full_path, index=False, encoding='utf-8')

print("Done!")
