import scrapy
import re

class LinkspiderSpider(scrapy.Spider):
    name = "linkspider"
    allowed_domains = ["internetconsultatie.nl"]
    start_urls = ["https://internetconsultatie.nl/zoeken/resultaat/full?TrefwoordenSearchScope=Titel&ConsultatiedatumVan=29-3-2023%2000%3A00%3A00&ConsultatiedatumTotEnMet=31-12-2023%2000%3A00%3A00"]
    page_number = 1
    
    def parse(self, response):
        # First page is special case
        first = True
        # Target the container that holds all the links
        container = response.css('div.result--list')

        # Extract links from within this container
        for link in container.css('a::attr(href)').getall():
            yield {
                'url': response.urljoin(link)
            }
        # Determine the current page number
        #current_page_number_match = re.search(r'/status/(\d+)', response.url)
        #current_page_number = int(current_page_number_match.group(1)) if current_page_number_match else 1

        # Increment the page number for the next page
        self.page_number = self.page_number + 1

        # Construct the URL for the next page
        next_page_url = response.urljoin(f"https://internetconsultatie.nl/zoeken/resultaat/full/status/{self.page_number}?TrefwoordenSearchScope=Titel&ConsultatiedatumVan=29-3-2023%2000%3A00%3A00&ConsultatiedatumTotEnMet=31-12-2023%2000%3A00%3A00")
        # Check if next page exists and make a request
        next_page_link = response.css('li.next a::attr(href)').get()
        if next_page_link:
            yield scrapy.Request(next_page_url, callback=self.parse)

