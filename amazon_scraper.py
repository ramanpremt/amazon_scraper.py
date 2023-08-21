import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape product details from a product listing page
def scrape_product_list_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []

        for product in soup.select('.s-asin .s-include-content-margin'):
            product_data = {}

            product_url = product.select_one('.a-link-normal.a-text-normal')['href']
            product_data['Product URL'] = f"https://www.amazon.in{product_url.strip()}"

            product_data['Product Name'] = product.select_one('.a-text-normal').get_text(strip=True)

            product_price = product.select_one('.a-offscreen')
            product_data['Product Price'] = product_price.get_text(strip=True) if product_price else 'N/A'

            product_rating = product.select_one('.a-icon-alt')
            product_data['Rating'] = product_rating.get_text(strip=True).split()[0] if product_rating else 'N/A'

            num_reviews = product.select_one('.a-size-base')
            product_data['Number of reviews'] = num_reviews.get_text(strip=True) if num_reviews else 'N/A'

            products.append(product_data)

        return products
    else:
        print(f"Failed to fetch {url}")
        return []

# Function to scrape additional details from a product page
def scrape_product_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        product_details = {}

        product_details['Description'] = soup.select_one('#productDescription p').get_text(strip=True)

        product_details['ASIN'] = soup.find('th', text='ASIN').find_next('td').get_text(strip=True)

        product_details['Product Description'] = soup.find('th', text='Product Description').find_next('td').get_text(strip=True)

        product_details['Manufacturer'] = soup.find('th', text='Manufacturer').find_next('td').get_text(strip=True)

        return product_details
    else:
        print(f"Failed to fetch {url}")
        return {}

# Main scraping process
if __name__ == "__main__":
    base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
    num_pages = 20
    products_list = []

    for page_num in range(1, num_pages + 1):
        page_url = f"{base_url}&page={page_num}"
        products_list.extend(scrape_product_list_page(page_url))

    for product in products_list:
        product_url = product['Product URL']
        additional_info = scrape_product_page(product_url)
        product.update(additional_info)

    # Export data to CSV
    csv_filename = "amazon_products.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of reviews', 'Description', 'ASIN', 'Product Description', 'Manufacturer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in products_list:
            writer.writerow(product)

    print(f"Data scraped and exported to {csv_filename}")
