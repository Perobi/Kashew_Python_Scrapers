import requests

def send_csv_to_api(file_path):
    url = "https://category-predictor-kashew-d27d988d97ff.herokuapp.com/predict"
    
    # Check if the CSV file exists and is accessible
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_path.split('/')[-1], file)}
            response = requests.post(url, files=files)

            # Check if the request was successful
            if response.status_code == 200:
                # Save the response content to a new CSV file in the current directory
                with open('output.csv', 'wb') as output_file:
                    output_file.write(response.content)
                return "File saved as output.csv"
            else:
                return f"Failed to get a valid response. Status code: {response.status_code}"

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    file_path = input("Enter the path to your CSV file: ")
    message = send_csv_to_api(file_path)
    print(message)
