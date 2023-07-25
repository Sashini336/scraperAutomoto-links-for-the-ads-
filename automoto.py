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
            title_element = car_item.find(
                'div', class_='col-md-4').find('h4').find('a', string=True)
            title = title_element.text.strip() if title_element else None

            price_element = car_item.find(
                'div', class_='result-item-pricing').find('div', class_='price')
            price = price_element.text.strip() if price_element else None

            fuel_element = car_item.find('div', class_='result-item-in').find_all('div', class_='col-md-12')[
                1].find('div', class_='result-item-features').find('ul', class_='inline').find_all('li')
            if len(fuel_element) >= 2:
                first_li_text = fuel_element[0].text.strip()
            else:
                first_li_text = None

            year_element = car_item.find(
                'div', class_='col-md-12').find('div', class_='col-md-2')
            year_text = year_element.text.strip() if year_element else None
            year = extract_year_from_string(year_text) if year_text else None

            image_element = car_item.find(
                'div', class_='result-item-image').find('a', class_='media-box').find('img', src=True)
            image = image_element['src'] if image_element and 'src' in image_element.attrs else None

            millage_elements = car_item.find('div', class_='result-item-in').find_all('div', class_='col-md-12')[
                1].find('div', class_='result-item-features').find('ul', class_='inline').find_all('li')
            if len(millage_elements) >= 2:
                second_li_text = millage_elements[1].text.strip()
            else:
                second_li_text = None

            region_elements = car_item.find('div', class_='result-item-in').find(
                'div', class_='col-md-12')[1].find('div', class_='col-md-3').find_all('div'[2])
            region = region_elements.text.strip() if title_element else None

            item_data = {
                'id': index,
                'title': title,
                'year': year,
                'price': price,
                'image': image,
                'millage': second_li_text,
                'fuel': first_li_text,
                'region': region,
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
    # Replace 'your_website_url_here' with the actual URL of your website
    website_url = "https://automoto.bg/listings/search?type_id=1&person=1&firm=2&coupe_id=3&door_id=&area_id=23&mark_id=&fuel_id=5&speed_id=4&condition_new=1&year_id=287&price_for=100000&price_to=&order=1"

    # Replace 'start_page_number' and 'end_page_number' with the range of pages you want to scrape (e.g., 1 to 5)
    start_page_number = 1
    end_page_number = 1

    scraped_data = scrape_multiple_pages(
        website_url, start_page_number, end_page_number)

    if scraped_data:
        # Print the scraped data
        for item in scraped_data:
            print(item)

        # Save the data to a JSON file
        with open("scraped_data.json", mode="w", encoding="utf-8") as file:
            json.dump(scraped_data, file, ensure_ascii=False, indent=4)

        print("Data saved to 'scraped_data.json'")
    else:
        print("Scraping failed. Please check the URL and try again.")
