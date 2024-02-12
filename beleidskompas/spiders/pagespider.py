import scrapy
import csv
import os

class ConsultationItem(scrapy.Item):
    Nummer = scrapy.Field()
    URL = scrapy.Field()
    Titel = scrapy.Field()
    Startdatum_consultatie = scrapy.Field()
    Einddatum_consultatie = scrapy.Field()
    Status = scrapy.Field()
    Type_consultatie = scrapy.Field()
    Organisatie = scrapy.Field()
    Keten_ID = scrapy.Field()
    Onderwerpen = scrapy.Field()
    Beleidskompas = scrapy.Field() # TODO
    IAK = scrapy.Field() # TODO
    # MINISTERIES
    

class PageSpider(scrapy.Spider):
    name = "pagespider"
    base_folder = 'data'  # Main folder to store all data
    page_number = 1

    def start_requests(self):
        # Replace 'links.csv' with your CSV file name
        with open('links.csv', 'r') as file:
            reader = csv.DictReader(file)
            for index, row in enumerate(reader, start=1):
                url = row['url']
                yield scrapy.Request(url, meta={'page_number': index})

    
    def parse(self, response):
        page_number = response.meta['page_number']  # Retrieve the current page number from meta
        item = ConsultationItem(Nummer=page_number)
        rows = response.xpath('//table[contains(@class, "table__data-overview")]/tbody/tr')
        for row in rows:
            header = row.xpath('th/text()').get().strip().replace(' ', '_').replace('.', '')
            if 'Onderwerpen' in header:
                # For 'Onderwerpen', specifically extract and concatenate all text from child nodes
                onderwerpen = row.xpath('.//th[contains(text(), "Onderwerpen")]/following-sibling::td//a/text()').getall()
                item['Onderwerpen'] = ', '.join(onderwerpen).strip()
            elif 'Keten_ID' in header:
                keten_id_link = row.xpath('.//th[contains(text(), "Keten-ID")]/following-sibling::td/a/@href').get()
                item['Keten_ID'] = keten_id_link.strip() if keten_id_link else None
            else:
                # General case for other fields
                value = row.xpath('td//text()').get().strip()

                # Dynamically assign values to item fields based on the header
                field_name = header.replace(' ', '_').replace('-', '').replace('.', '')
                if field_name in item.fields:
                    item[field_name] = value
                else:
                    self.logger.warning(f"Undefined field for header: {header}")

        item['Beleidskompas'] = False
        item['IAK'] = False
        # Search for 'beleidskompas' in list items
        list_items = response.xpath('//ul[@id="113"]/li')
        for li in list_items:
            # Extract text from each list item and perform a case-insensitive search
            text = li.xpath('.//text()').getall()
            text = ' '.join(text)  # Combine list elements into a single string
            if 'beleidskompas' in text.lower():  # Case-insensitive check
                item['Beleidskompas'] = True
            if 'iak' in text.lower():
                item['IAK'] = True

        item['URL'] = response.url

        # Extract the title using XPath
        title = response.xpath('//div[contains(@class, "row--contentheading")]/h1/text()').get().strip()
        item['Titel'] = title

        yield item
