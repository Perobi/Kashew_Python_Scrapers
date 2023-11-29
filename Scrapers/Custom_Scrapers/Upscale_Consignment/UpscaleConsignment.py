from bs4 import BeautifulSoup
import requests
from bs4 import NavigableString
import pandas as pd
import os

directory_path = '/Users/perobiora/Desktop/Kashew/PythonScraper/Output/'
filename = 'Upscale_Consignment.csv'

full_path = directory_path + filename

titles = []
descriptions = []
prices = []
skus = []
images = []
heights = []
widths = []
depths = []
brands = []
categories = []

# Iterate over all the pages
for i in range(1, 17):
    if i == 1:
        website = "https://upscaleconsignment.com/furniture"
    else:
        website = f"https://upscaleconsignment.com/furniture/index{i}.html"

    response = requests.get(website)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    product_box = soup.find('ul', class_='grid_view row_view')

    links = set()  # Use a set instead of a list

    for link in product_box.find_all('a', href=True):
        links.add(link['href'])  # Use add instead of append

    for link in links:
        if not link.startswith('/'):
            link = '/' + link
        response = requests.get(f'https://upscaleconsignment.com{link}')
        content = response.text
        soup = BeautifulSoup(content, 'lxml')
        product_info = soup.find('div', class_='col-xs-12 col-md-6')
        table = soup.find('table', class_='table')

        # Title
        titles.append(product_info.find('h1').text if product_info.find('h1') else '')

        # Brand
        brands.append(product_info.find('span', itemprop='name').text if product_info.find('span', itemprop='name') else '')

        # Description, SKU, Category
        description = ''
        sku = ''
        category = ''

        description_span = product_info.find('span', itemprop='description')
        if description_span:
            for i, content in enumerate(description_span.contents):
                if isinstance(content, NavigableString):
                    text = str(content).strip()
                    if text:
                        if description_span.contents[i - 1].text.strip() == 'Item ID:':
                            sku = text
                        elif description_span.contents[i - 1].text.strip() == 'Category:':
                            category = text
                        else:
                            description = text

        descriptions.append(description)
        skus.append(sku)
        categories.append(category)

        # Price
        price_span = product_info.find('span', id='product_price')
        prices.append(price_span.text.strip() if price_span else '')

        # Images
        thumb_slider_div = soup.find('div', id='thumb_slider')
        product_images = []
        if thumb_slider_div:
            # find all 'img' tags within the div
            img_tags = thumb_slider_div.find_all('img')

            # iterate over the img tags, remove '_t' from the src and append to the list
            for img in img_tags:
                if 'src' in img.attrs:
                    cleaned_img_src = img['src'].replace('_t', '')
                    product_images.append(cleaned_img_src)

        # Convert the list of product images to a single string
        image_string = ', '.join(product_images)
        images.append(image_string)

        # Dimensions
        width = ''
        depth = ''
        height = ''

        if table:
            # find all 'tr' tags within the table
            tr_tags = table.find_all('tr')

            # check if there are at least three 'tr' tags
            if len(tr_tags) >= 3:
                # find all 'td' tags within the third 'tr' tag
                td_tags = tr_tags[2].find_all('td')

                # check if there are at least three 'td' tags
                if len(td_tags) >= 3:
                    # the first 'td' contains the width
                    width = td_tags[0].text

                    # the second 'td' contains the depth
                    depth = td_tags[1].text

                    # the third 'td' contains the height
                    height = td_tags[2].text

        widths.append(width)
        depths.append(depth)
        heights.append(height)

        print(f'Finished scraping {titles[-1]} - {skus[-1]} - {categories[-1]} - {brands[-1]} - {prices[-1]} - {images[-1]} - {widths[-1]} - {depths[-1]} - {heights[-1]} ')

# Create a dictionary where keys are column names and values are the lists of data
data = {
    'title': titles,
    'description': descriptions,
    'price': prices,
    'sku': skus,
    'images': images,
    'width': widths,
    'depth': depths,
    'height': heights,
    'category': categories,
    'brand': brands
}

# Create a pandas dataframe from the dictionary
df = pd.DataFrame(data)

# Save the dataframe to a CSV file
df.to_csv(full_path, index=False)
print("Done")