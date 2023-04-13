import json
import re

import scrapy

from ..items import ProductItem


class JbhifiProductSpider(scrapy.Spider):
    name = 'jbhifi_product'
    allowed_domains = ['jbhifi.com.au']

    def __init__(self, product_url, **kwargs):
        super().__init__(**kwargs)
        self.product_url = product_url

    def start_requests(self):
        yield scrapy.Request(self.product_url, callback=self.parse_product)

    def parse_product(self, response):
        product_from_script = re.findall(
            'window.themeConfig\(\'product\',\s*({.*?})\)\;', response.text, re.DOTALL)
        product_json = json.loads(product_from_script[0])

        product_meta_from_script = re.findall(
            'window.themeConfig\(\'product\.metafields\',\s*({.*?})\)\;', response.text, re.DOTALL)
        product_meta_json = json.loads(product_meta_from_script[0])

        item = ProductItem()
        item['title'] = product_json.get('title')
        item['url'] = response.url

        mark_price = product_json.get('compare_at_price')
        if mark_price:
            item['mark_price'] = product_json.get('compare_at_price') / 100
        else:
            item['mark_price'] = mark_price

        item['sale_price'] = product_json.get('price') / 100
        item['sku'] = product_json.get('variants', [{}])[0].get('sku')
        item['description'] = product_json.get('description')

        display = product_meta_json.get('online_product', {}).get(
            'value', {}).get('Display', {})
        item['review_count'] = display.get('NumberOfProductReviews')
        item['average_rating'] = display.get('AverageProductReviewRating')
        item['main_image'] = response.urljoin(
            product_json.get('featured_image'))
        item['images'] = [response.urljoin(
            image) for image in product_json.get('images', [{}])]
        item['source'] = 'JB Hi-Fi'
        item['in_stock'] = product_json.get('available')
        return item
