import scrapy
from scrapy import Request
import csv
import os

class DocspiderSpider(scrapy.Spider):
    name = "docspider"
    base_folder = 'data'  # Main folder to store all data
    counter = 1

    def start_requests(self):
        # Replace 'links.csv' with your CSV file name
        with open('links.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                url = row['url']
                yield scrapy.Request(url, self.parse, meta={'counter': self.counter})
                self.counter += 1
    
    # def parse(self, response):
    #     pdf_links = response.css('ul.list--sources a::attr(href)').getall()
    #     for link in pdf_links:
    #         full_link = response.urljoin(link)
    #         # Call a new function to handle PDF downloading
    #         yield scrapy.Request(full_link, callback=self.save_pdf, meta={'parent_url': response.url, 'counter': response.meta['counter']})

    def parse(self, response):
        items = response.css('ul.list--sources > li')
        for item in items:
            title = item.css('div.list--source__information::text').extract_first().strip()
            link = item.css('a::attr(href)').get()
            full_link = response.urljoin(link)
            yield scrapy.Request(full_link, callback=self.save_pdf, meta={'parent_url': response.url, 'counter': response.meta['counter'], 'title': title})
            
    def save_pdf(self, response):
        title = response.meta['title']
        sanitized_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
        file_name = f"{response.meta['counter']}_{sanitized_title}.pdf"
        folder_name = str(response.meta['counter'])
        # Create a subfolder within the 'data' folder
        full_folder_path = os.path.join(self.base_folder, folder_name)
        os.makedirs(full_folder_path, exist_ok=True)  # Create folder if it doesn't exist

        file_path = os.path.join(full_folder_path, file_name)

        self.logger.info('Saving PDF %s', file_path)
        with open(file_path, 'wb') as file:
            file.write(response.body)

