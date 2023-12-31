import requests
from bs4 import BeautifulSoup
import time
import json
import re


def extract_year_from_string(s):
    pattern = r'\b\d{4}\b'
    matches = re.findall(pattern, s)
    return matches[0] if matches else None


def scrape_website(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        # Send a GET request to the website with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for any errors in the response

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the container with the search results
        results_container = soup.find('div', class_='results-container-in')

        # Find all the car listing items
        car_items = results_container.find_all(
            'div', class_='result-item format-standard')

        # Extract title, region, and prices
        scraped_data = []
        for index, car_item in enumerate(car_items, start=1):
            path_element = car_item.find('a', href=True)
            path = path_element['href'] if path_element else None

            item_data = {
                'path': path
            }
            scraped_data.append(item_data)

            # Add a delay of 1 second between requests to be more gentle to the server
            time.sleep(1)

        return scraped_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")
        return None


def get_total_pages(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    page_links = soup.find('ul', class_='pagination').find_all('li')
    # The second to last page link is the last page number
    last_page = int(page_links[-2].text.strip())
    return last_page


def scrape_multiple_pages(base_url, start_page, end_page):
    try:
        print(f"Scraping data from page {start_page} to page {end_page}...")
        all_data = []
        for page in range(start_page, end_page + 1):
            page_url = f"{base_url}&page={page}"
            page_data = scrape_website(page_url)
            if page_data:
                all_data.extend(page_data)
        return all_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")
        return None


if __name__ == "__main__":
    # Get the URL and number of pages from the console
    website_url = input("Enter the URL of the website to scrape: ")
    start_page_number = int(input("Enter the starting page number: "))
    end_page_number = int(input("Enter the ending page number: "))

    scraped_data = scrape_multiple_pages(
        website_url, start_page_number, end_page_number)

    if scraped_data:
        # Print the scraped data

        # Specify the folder path for saving the JSON file
        folder_path = "/Users/a.petkov/Desktop/TrainingGuides/Car"

        # Save the data to a JSON file in the specified folder path
        file_path = f"{folder_path}/data.json"
        with open(file_path, mode="w", encoding="utf-8") as file:
            json.dump(scraped_data, file, ensure_ascii=False, indent=4)

        print(f"Data saved to '{file_path}'")
    else:
        print("Scraping failed. Please check the URL and try again.")
