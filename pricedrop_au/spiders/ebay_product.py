import scrapy
from scrapy import Request
from ..items import ProductItem
import re
from ..utils import *


class EbayProductSpider(scrapy.Spider):
    name = 'ebay_product'
    allowed_domains = ['ebay.com.au']

    def __init__(self, product_url, **kwargs):
        super().__init__(**kwargs)
        self.product_url = product_url

    def start_requests(self):
        yield Request(url=self.product_url)

    def parse(self, response):
        item = ProductItem()
        item['title'] = response.css('span#vi-lkhdr-itmTitl::text').get()
        item['source'] = 'ebay'
        item['url'] = response.url
        item['sku'] = re.findall(
            '[p|itm]/(\d+)', self.product_url)
        try:
            item['mark_price'] = get_float_or_none(response.css(
                'span.ux-textspans.ux-textspans--STRIKETHROUGH::text').get().strip().replace('AU $', ''))
        except:
            item['mark_price'] = ''
        item['sale_price'] = get_float_or_none(response.css(
            'span[itemprop="price"] span::text').get().replace('AU $', ''))
        item['description'] = response.css(
            'meta[name="description"]::attr(content)').get()
        instock = response.css(
            'span[itemprop="availability"]::attr(content)').get().split('/')[3]
        if 'instock' in instock.lower():
            item['in_stock'] = True
        else:
            item['in_stock'] = False

        item['main_image'] = response.css(
            'div.ux-image-carousel img::attr(src)').get()
        item['images'] = response.css(
            'div.ux-image-carousel img::attr(data-src)').extract()

        return item
