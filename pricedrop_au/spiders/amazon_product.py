import json
import re

import scrapy
from ..items import ProductItem
from ..utils import get_float_or_none, get_int_or_none


class AmazonProductSpider(scrapy.Spider):
    name = 'amazon_product'
    allowed_domains = ['amazon.com.au']

    def __init__(self, product_url, **kwargs):
        super().__init__(**kwargs)
        self.product_url = product_url

    def start_requests(self):
        yield scrapy.Request(url=self.product_url, callback=self.parse_product)

    def parse_product(self, response):
        item = ProductItem()
        item['title'] = response.css('h1#title span::text').get().replace('\xa0', '').strip()
        item['url'] = response.url
        item['mark_price'] = get_float_or_none(response.css('span[data-a-size="s"] span::text').get())
        item['sale_price'] = get_float_or_none(response.css('span.a-offscreen::text').get())
        item['description'] = item['title']
        item['sku'] = response.css('link[rel="canonical"]::attr(href)').get().split('/dp/')[1]
        item['average_rating'] = get_float_or_none(response.css('span.a-icon-alt::text').get('').split()[0])
        item['review_count'] = get_int_or_none(response.css('span#acrCustomerReviewText::text').get())

        try:
            data = json.loads(re.findall("jQuery.parseJSON\('(.*?)'\);", response.text)[0])
        except:
            data = json.loads(re.findall("jQuery.parseJSON\('(.*?)'\);", response.text)[0].replace('\\', ''))

        item['images'] = [x.get('hiRes') for x in data.get('colorImages', {}).get(data.get('landingAsinColor', ''), [])]

        if len(item['images']) == 0:
            item['images'] = re.findall('"hiRes"\s*:\s*"(.*?)"', response.text, re.I)

        if len(item['images']) > 0:
            item['main_image'] = item['images'][0]
        item['source'] = 'Amazon'

        stock_message = response.css('div#availability span::text').get('').replace('.', '').strip().lower()
        item['in_stock'] = 'in stock' in stock_message
        return item
