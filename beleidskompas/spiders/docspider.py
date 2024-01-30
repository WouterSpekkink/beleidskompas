import scrapy
from scrapy import Request
import csv
import os

class DocspiderSpider(scrapy.Spider):
    name = "docspider"
    base_folder = 'data'  # Main folder to store all data

    def start_requests(self):
        # Replace 'links.csv' with your CSV file name
        with open('links.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                url = row['url']
                yield scrapy.Request(url, self.parse)
    
    allowed_domains = ["internetconsultatie.nl"]
    start_urls = ["https://internetconsultatie.nl"]

    def parse(self, response):
        pdf_links = response.css('ul.list--sources a::attr(href)').getall()
        for link in pdf_links:
            full_link = response.urljoin(link)
            # Call a new function to handle PDF downloading
            yield scrapy.Request(full_link, callback=self.save_pdf, meta={'parent_url': response.url})

    def save_pdf(self, response):
        parent_url = response.meta['parent_url']
        folder_name = self.get_folder_name(parent_url)
        # Create a subfolder within the 'data' folder
        full_folder_path = os.path.join(self.base_folder, folder_name)
        os.makedirs(full_folder_path, exist_ok=True)  # Create folder if it doesn't exist

        file_name = response.url.split('/')[-1] + '.pdf'
        file_path = os.path.join(full_folder_path, file_name)

        self.logger.info('Saving PDF %s', file_path)
        with open(file_path, 'wb') as file:
            file.write(response.body)

    def get_folder_name(self, url):
        # Extract a suitable folder name from the URL
        # This is just an example, adjust the logic as per your requirement
        folder_name = url.split('/')[-2]  # Or some other logic to derive folder name
        return folder_name

            
