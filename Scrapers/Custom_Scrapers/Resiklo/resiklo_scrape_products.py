from selenium import webdriver
import time

website = 'https://resiklodesign.com/shop'

driver = webdriver.Chrome()

driver.get(website)

time.sleep(3)


# product container
product_container = driver.find_element("",'//div[@id="yui_3_17_2_1_1687446175170_2547"]')
all_links = product_container.find_elements("xpath",'.//a')

for link in all_links:  
    print(link.get_attribute('href'))

