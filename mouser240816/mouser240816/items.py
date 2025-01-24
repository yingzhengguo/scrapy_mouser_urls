# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Mouser240816Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    mfr_name = scrapy.Field()
    mfr_link = scrapy.Field()
    all_products_url = scrapy.Field()
