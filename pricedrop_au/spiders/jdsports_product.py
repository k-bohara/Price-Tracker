import json
import re

import scrapy

from ..items import ProductItem


class JbhifiProductSpider(scrapy.Spider):
    name = 'jdsports_product'
    allowed_domains = ['jd-sports.com.au', 'powerreviews.com']

    start_urls = ["https://www.jd-sports.com.au/sale/"]

    def parse(self, response):
        products = response.css('li.productListItem')
        for product in products:
            product_url = response.urljoin(
                product.css('a.itemImage::attr(href)').get())
            yield scrapy.Request(product_url, callback=self.parse_product)

        next_page = response.css(
            'div.pageLinks a[rel="next"]::attr(href)').get()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

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

        merch_id = response.css(
            'input[name="POWER_REVIEWS_MERCH_ID"]::attr(value)').get()
        apikey = response.css(
            'input[name="POWER_REVIEWS_API_KEY"]::attr(value)').get()
        prod_id = data['id']
        url = f'https://display.powerreviews.com/m/{merch_id}/l/all/product/{prod_id}/reviews?apikey={apikey}&_noconfig=true&page_locale=en_AU'
        yield scrapy.Request(url, callback=self.parse_review, meta={'item': item})

    def parse_review(self, response):
        data = json.loads(response.text)
        item = response.meta.get('item', {})
        try:
            item['average_rating'] = data['results'][0]['rollup']['page_brand_score']['average_rating']
        except:
            item['average_rating'] = None

        try:
            item['review_count'] = data['results'][0]['rollup']['page_brand_score']['published_review_count']
        except:
            item['review_count'] = None
        return item
