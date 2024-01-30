import scrapy


class LinkspiderSpider(scrapy.Spider):
    name = "linkspider"
    allowed_domains = ["internetconsultatie.nl"]
    start_urls = ["https://internetconsultatie.nl/zoeken/resultaat/full?TrefwoordenSearchScope=Titel"]

    def parse(self, response):
        pass
