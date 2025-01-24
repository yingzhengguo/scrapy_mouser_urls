import re
import scrapy
import pymysql
import logging
from scrapy import Request, Selector
from mouser240816.items import Mouser240816Item

class MouserSpider(scrapy.Spider):
    name = "mouser"
    allowed_domains = ["www.mouser.cn"]
    start_urls = ["https://www.mouser.cn/manufacturer"]
    logger = logging.getLogger(__name__)
    def start_requests(self, **kwargs):
        yield Request(
            url=self.start_urls[0], callback=self.parse,
        )
    def parse(self, response, **kwargs):
        lis = response.xpath('//div[@class="mfr_group"]'
                             # '[@id="group_nbr"]'
                             '[@id="group_A"]'
                             '//li')#//*[@id="group_nbr"]/ul/li
        for li in lis:
            mouser_item = Mouser240816Item()
            mfr_name = li.xpath('.//a/@title').get()
            mouser_item['mfr_name'] = re.sub(r'\s+', '', mfr_name)
            mfr_urls = li.xpath('.//a/@href')
            for mfr_links in mfr_urls:
                mouser_item['mfr_link'] = response.urljoin(mfr_links.extract())
                if mouser_item['mfr_link']:
                    yield Request(url=mouser_item['mfr_link'], callback=self.parse_prolink,
                                  cb_kwargs={'item': mouser_item},)  # 传递 item 到下一个回调函数
                # yield mouser_item
                # else:
                #     self.logger.error('mfr_link is None')
    def parse_prolink(self, response, **kwargs):
        mouser_item = kwargs['item']
        all_products_url =response.xpath('//*[@id="sidebar"]/div[@class="all_products"]/a/@href')
        if all_products_url:
            for all_products_urls in all_products_url:
                mouser_item['all_products_url'] = response.urljoin(all_products_urls.extract())
        else:
            mouser_item['all_products_url'] = ''
            self.logger.error('all_products_url is None')
        yield mouser_item