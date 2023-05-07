import json

import scrapy
from scrapy import Request

from ..items import ProductItem
from ..utils import get_float_or_none


class CostcoProductSpider(scrapy.Spider):
    name = 'costco_product'
    allowed_domains = ['costco.com.au', 'bazaarvoice.com']

    headers = {'authority': 'www.costco.com.au',
               'accept': 'application/json, text/plain, */*',
               'accept-language': 'en-US,en;q=0.9',
               'content-type': 'application/json'}

    def start_requests(self):
        url = 'https://www.costco.com.au/rest/v2/australia/products/search?fields=FULL&query=&pageSize=48&category=hot-buys&lang=en_AU&curr=AUD'
        yield scrapy.Request(url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        data = json.loads(response.text)
        products = data.get('products', []) or []

        for product in products:
            product_url = response.urljoin(product['url'])
            yield Request(url=product_url, callback=self.parse_product)

        total_pages = data.get('pagination', {}).get('totalPages', 1)
        current_page = data.get('pagination', {}).get('currentPage', 2)

        if current_page < total_pages and len(products) > 0:
            url = f'https://www.costco.com.au/rest/v2/australia/products/search?fields=FULL&query=&pageSize=48&currentPage={current_page+1}&category=hot-buys&lang=en_AU&curr=AUD'

            yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_product(self, response):
        data = response.css('script#schemaorg_product::text').get()
        json_data = json.loads(data)
        item = ProductItem()
        item['title'] = json_data.get('name')
        item['url'] = response.url
        item['description'] = ''.join(response.css(
            'div.product-detail-dsc ::text').extract()).strip()
        item['source'] = 'Costco'
        item['sku'] = json_data.get('sku')
        item['sale_price'] = json_data.get('offers').get('price')
        in_stock = json_data.get('offers', {}).get(
            'availability', '').split('/')[-1]
        if 'instock' in in_stock.lower():
            item['in_stock'] = True
        else:
            item['in_stock'] = False
        item['mark_price'] = get_float_or_none(response.css(
            'span.notranslate.ng-star-inserted::text').get())
        item['main_image'] = json_data.get('image')
        item['images'] = []
        sku = item['sku']
        feedback_url = f'https://api.bazaarvoice.com/data/display/0.2alpha/product/summary?PassKey=caBZhTkDXtH0cKNQs4zqF7kFJeuy36nFrcL8OsEfpxt98&productid={sku}&contentType=reviews,questions&reviewDistribution=primaryRating,recommended&rev=0&contentlocale=en*,en_AU'
        yield Request(url=feedback_url, callback=self.parse_feedback, meta={'item': item}, dont_filter=True)

    def parse_feedback(self, response):
        item = response.meta.get('item')
        data = json.loads(response.text)
        item['average_rating'] = data.get('reviewSummary', {}).get(
            'primaryRating', {}).get('average')
        item['review_count'] = data.get('reviewSummary', {}).get('numReviews')
        return item
