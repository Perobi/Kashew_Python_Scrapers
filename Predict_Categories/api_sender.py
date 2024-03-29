import requests
import csv

def format_images(images):
    return images.replace("'", "").replace("[", "").replace("]", "")

def send_titles_to_api_and_save_response(file_path, title_column):
    url = "https://newish-categorizer-api-99887e6c4621.herokuapp.com/predict"
    
    try:
        with open(file_path, 'r') as csvfile, open('output.csv', 'w', newline='') as output_csv:
            reader = csv.DictReader(csvfile)
            fieldnames = [fieldname for fieldname in reader.fieldnames if fieldname not in ['category', 'sub_category']] + ['predicted_category', 'predicted_sub_category', 'predicted_type']
            writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                title = row[title_column]
                response = requests.post(url, json={"title": title})

                if response.status_code == 200:
                    data = response.json()
                    row['predicted_category'] = data.get('category', 'Failed')
                    row['predicted_sub_category'] = data.get('sub_category', 'Failed')
                    row['predicted_type'] = data.get('type', 'Failed')
                else:
                    row['predicted_category'] = 'Failed'
                    row['predicted_sub_category'] = 'Failed'
                    row['predicted_type'] = 'Failed'
                    print(f"API request failed for title: {title}")

                row['images'] = format_images(row['images'])
                del row['category']
                del row['sub_category']
                writer.writerow(row)
                print(f"Row processed: {title}")

        return "Output CSV file created successfully."

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    file_path = input("Enter the path to your CSV file: ")
    title_column = input("Enter the name of the column containing titles: ")
    message = send_titles_to_api_and_save_response(file_path, title_column)
    print(message)
