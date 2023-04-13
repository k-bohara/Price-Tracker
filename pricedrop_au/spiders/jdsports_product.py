import json
import re

import scrapy

from ..items import ProductItem


class JbhifiProductSpider(scrapy.Spider):
    name = 'jdsports_product'
    allowed_domains = ['jd-sports.com.au', 'powerreviews.com']

    def __init__(self, product_url, **kwargs):
        super().__init__(**kwargs)
        self.product_url = product_url

    def start_requests(self):
        yield scrapy.Request(self.product_url, callback=self.parse_product)

    def parse_product(self, response):
        data = response.css('script[type="application/ld+json"]::text').get()
        data = json.loads(data)
        item = ProductItem()
        item['title'] = data['name']
        item['url'] = data['offers']['url']
        item['source'] = data['offers']['seller']['name']
        item['sale_price'] = data['offers']['price']

        offers = data['offers']
        if isinstance(offers, list):
            in_stock = data['offers'][0]['availability']
        elif isinstance(offers, dict):
            in_stock = data['offers']['availability']
        else:
            in_stock = ''

        if 'instock' in in_stock.lower():
            item['in_stock'] = True
        else:
            item['in_stock'] = False

        item['sku'] = data['sku']
        item['description'] = data['description']
        item['images'] = data['image']
        item['main_image'] = data['image'][0]
        try:
            item['mark_price'] = response.css(
                'div.itemPrices span.was span::text').get().replace('$', '')
        except:
            item['mark_price'] = None

        # for review and ratings
        apikey = 'dabd60c9-3110-4a4f-afd3-5a6f6f0dd781'

        merch_id = response.css('input[name="POWER_REVIEWS_MERCH_ID"]::attr(value)').get()
        apikey = response.css('input[name="POWER_REVIEWS_API_KEY"]::attr(value)').get()
        prod_id = data['id']
        url = f'https://display.powerreviews.com/m/{merch_id}/l/all/product/{prod_id}/reviews?apikey={apikey}&_noconfig=true&page_locale=en_AU'
        yield scrapy.Request(url, callback=self.parse_review, meta={'item': item})

    def parse_review(self, response):
        data = json.loads(response.text)
        item = response.meta.get('item', {})
        item['average_rating'] = data['results'][0]['rollup']['average_rating']
        item['review_count'] = data['results'][0]['rollup']['review_count']
        return item
