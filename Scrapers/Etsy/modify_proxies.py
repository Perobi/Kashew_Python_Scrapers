import os

# Define the path to the original file
original_file_path = '/Users/perobiora/Desktop/Kashew/PythonScraper/Scrapers/Etsy/http_proxies.txt'

# Read the list of proxies from your original file
with open(original_file_path, 'r') as file:
    original_proxies = file.read().splitlines()

# Construct the path to the new file in the same directory
new_file_path = os.path.join(os.path.dirname(original_file_path), 'us_http_proxies.txt')

# Create a new file in the same directory to save the proxies in the correct format
with open(new_file_path, 'w') as new_file:
    for proxy in original_proxies:
        # Add 'http://' and 'https://' prefixes to each proxy and write them to the new file
        new_file.write(f"http://{proxy}\n")
        new_file.write(f"https://{proxy}\n")

print("Proxies have been converted to the correct format and saved in 'us_http_proxies.txt' in the same directory.")
