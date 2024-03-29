from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from fake_useragent import UserAgent
import random
import pandas as pd
import time
from selenium.webdriver.common.by import By
from requests_proxyport import Session  # Importing from requests_proxyport
from fake_useragent import UserAgent

# List of proxy URLs from your text file
with open('/Users/perobiora/Desktop/Kashew/PythonScraper/Scrapers/Etsy/us_http_proxies.txt', 'r') as file:
    proxies = [{'http': proxy, 'https': proxy} for proxy in file.read().splitlines()]

headers = {
    'User-Agent': UserAgent().random,
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'

}

root = "https://www.etsy.com/shop"
profile = "/ellewoodworthy"
website_template = root + profile + "?page={page}#items"

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-webrtc')


# Initialize the Chrome driver with the options
driver = webdriver.Chrome(options=chrome_options)

session = Session(proxyport_api_key='a0d72032-4d93-4909-b298-54cdee98b570')  # Replace 'your_api_key_here' with your actual API key

links = []  # Initialize the links list outside the loop

data = {'title':[], 'sku':[], 'price':[], 'category':[], 'condition':[], 'width':[], 'height':[], 'depth':[], 'description':[], 'tags':[], 'images':[]}

for page in range(1, 10):  # We start at 1 and go up to (but not including) 9, so this gives us 1-8
    website = website_template.format(page=page)
    driver.get(website)

    if page == 1:
        time.sleep(15)
    else:
        time.sleep(random.uniform(2, 5)) 
    


    WebDriverWait(driver, 10).until(EC.presence_of_element_located(("xpath", '//div[@class="wt-pr-xs-0 wt-pl-xs-0 shop-home-wider-items wt-pb-xs-5"]')))
    main_container = driver.find_element("xpath", '//div[@class="wt-pr-xs-0 wt-pl-xs-0 shop-home-wider-items wt-pb-xs-5"]')    
    listings_container = main_container.find_element("xpath", '//div[@data-listings-container]')
    all_items = listings_container.find_elements("xpath", '//div[@data-behat-listing-card]')
    
    for value in all_items: 
        links.append(value.find_element("xpath", './/a').get_attribute('href'))
       
            
count = 0
for url in links: 
    time.sleep(random.uniform(2, 5)) 
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
        
    if len(path_parts) > 2 and path_parts[1] == 'listing':
        sku = path_parts[2]
        data['sku'].append(sku)
        print("sku: ", data['sku'][-1])
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(("xpath", '//div[@class="body-wrap wt-body-max-width wt-display-flex-md wt-flex-direction-column-xs"]')))


        listing_container = driver.find_element("xpath",'//div[@class="body-wrap wt-body-max-width wt-display-flex-md wt-flex-direction-column-xs"]')

        # -------------------Listing Title-------------------
        try:
            data['title'].append(listing_container.find_element("xpath",'//h1[@data-buy-box-listing-title="true"]').text)
        except:
            data['title'].append("")
            print("failed to get title")

        # -------------------Listing Price-------------------
        try:
            price_element = listing_container.find_element("xpath",'//div[@data-buy-box-region="price"]')
            try: 
                price_el = price_element.find_element("xpath",'//p[@class="wt-text-title-larger wt-mr-xs-1 "]').text
            except: 
                price_el = price_element.find_element("xpath",'//p[@class="wt-text-title-larger wt-mr-xs-1 wt-text-slime"]').text
            currency_value = price_el.split("\n")[1][1:]
            data['price'].append(currency_value)
            print("price: ", data['price'][-1])
        except:
            data['price'].append("")
            print("failed to get price")


        try:
            # Get the container with all the list elements
            category_element = listing_container.find_element('xpath','//ul[@class="wt-list-unstyled wt-grid__item-xs-12 wt-body-max-width wt-display-flex-xs wt-justify-content-center"]')
            
            # Find all 'li' elements within the 'ul'
            li_elements = category_element.find_elements('xpath','./li')
            
            # Get the last 'li' element and its text
            last_li = li_elements[-1]
            last_li_text = last_li.find_element('xpath', "./a").text
            data['category'].append(last_li_text)  
            print("category: ", data['category'][-1])              
        except:
            data['category'].append("")  
            print("failed to get category")


        # -------------------Listing Condition-------------------
        data['condition'].append("Very Good")

        # -------------------Listing Dimensions-------------------
        try:
            dimensions_box = listing_container.find_element("xpath",'//ul[@class="wt-block-grid-xs-1 wt-text-body-01 show-icons wt-mt-xs-1 wt-pl-xs-0 wt-mb-xs-3"]')
            dimensions = dimensions_box.find_element("xpath",'./li[3]')
            dadm = dimensions.find_element("xpath",'./div[2]')
            dimensions_divs = dadm.find_elements("xpath",'./div[@class="wt-ml-xs-1"]')
            width, height, depth = "", "", ""
            for dim in dimensions_divs:
                try:
                    dimension_name = dim.text.split(":")[0].strip().lower()
                    dimension_value = float(dim.text.split(":")[1].strip().split(" ")[0])
                
                    if dimension_name == 'width' or dimension_name == 'overall width':
                        width = dimension_value
                    elif dimension_name == 'height' or dimension_name == 'overall height':
                        height = dimension_value
                    elif dimension_name == 'depth' or dimension_name == 'overall depth':
                        depth = dimension_value
                except Exception as e:
                    print(f"Failed to process dimension: {dim.text}. Error: {str(e)}")
            data['width'].append(width)
            data['height'].append(height)
            data['depth'].append(depth)
            print("dimensions: ", data['width'][-1], data['height'][-1], data['depth'][-1])
        except:
            data['width'].append("")
            data['height'].append("")
            data['depth'].append("")
            print("failed to get dimensions")

        # -------------------Listing Description-------------------
        try:
            description_box = listing_container.find_element("xpath",'//p[@data-product-details-description-text-content]')
            description_text = description_box.text

            # split the description into paragraphs
            paragraphs = description_text.split('\n')

            # create a list to store the paragraphs we want to keep
            description_filtered = []

            for paragraph in paragraphs:
                # remove the return policy
                if "RETURNS" in paragraph:
                    continue
                # remove paragraph with phone number
                if "You may also call or text me at" in paragraph:
                    continue
                if "call" in paragraph or "text" in paragraph or "Call" in paragraph or "Text" in paragraph or "239-560-200" in paragraph or "meet" in paragraph or "Fort Myers" in paragraph or "FREE" in paragraph:
                    continue
                # remove shipping info
                if "SHIPPING" in paragraph or "LOCAL PICKUP" in paragraph or "We can meet locally" in paragraph or "Shipping" in paragraph or "Cancellations" in paragraph or "returns" in paragraph or "I also have" in paragraph or "etsy" in paragraph:
                    continue
                if "message" in paragraph or "cancellations" in paragraph or "return" in paragraph or "returns" in paragraph:
                    continue
                # remove empty lines or lines only containing whitespace
                if paragraph.strip() == '':
                    continue
                # if none of the above conditions were met, add the paragraph to our list
                description_filtered.append(paragraph)

            # join the paragraphs back together into a single string
            description_final = "\n".join(description_filtered)

            # add to the descriptions list
            data['description'].append(description_final) # removing the trailing new line
        except:
            data['description'].append("")
            print("failed to get description")

        # -------------------Listing Tags-------------------
        try:
            tag_container = listing_container.find_element("xpath",'//p[@id="legacy-materials-product-details"]')
            tag_text = tag_container.text

            # Split the text at the colon and strip whitespace from the second part
            tag = tag_text.split(":")[1].strip()

            # Append to the tags list
            data['tags'].append(tag)
        except:
            data['tags'].append("")
            print("failed to get tags")

        # -------------------Listing Images-------------------
        try:
            image_container = listing_container.find_element("xpath",'//div[@data-component="listing-page-image-carousel"]')
            image_elements = image_container.find_elements(By.TAG_NAME, 'img')
            image_links = []
            for image in image_elements:
                # Extracting the 'src' attribute
                raw_link = image.get_attribute('src')
                
                # Modifying the URL string to replace _75x75 with _1200x1200
                modified_link = raw_link.replace('_75x75', '_1200x1200')
                
                image_links.append(modified_link)
            data['images'].append(image_links)
        except:
            data['images'].append([])
            print("failed to get images")
        count += 1
        print ("finished scraping ", count, " of ", len(links))
        print("done scraping listing title: ", data['title'][-1])

    except Exception as e:
        print(f"An error occurred on page: {url}. Error: {str(e)}. Skipping to next URL.")
        print("failed to get listing for reason: ", str(e))
        continue
# Once the loop is done, convert your dictionary into a pandas DataFrame
df = pd.DataFrame(data)

file_name = f"{profile}.csv"
directory_path = "/Users/perobiora/Desktop/Kashew/PythonScraper/Output/"

full_path = directory_path + file_name
df.to_csv(full_path, index=False, encoding='utf-8')
 
driver.quit()