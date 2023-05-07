import json
import re
from urllib.parse import urljoin

import scrapy

from ..items import ProductItem


class JbhifiProductSpider(scrapy.Spider):
    name = 'jbhifi_product'
    allowed_domains = ['jbhifi.com.au', 'algolia.net']

    def __init__(self, product_url=None, **kwargs):
        super().__init__(**kwargs)
        self.product_url = product_url

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'x-algolia-api-key': '1d989f0839a992bbece9099e1b091f07',
        'x-algolia-application-id': 'VTVKM5URPX'
    }
    algolia_url = 'https://vtvkm5urpx-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.2)%3B%20Browser%3B%20JS%20Helper%20(3.11.1)%3B%20react%20(16.14.0)%3B%20react-instantsearch%20(6.38.1)'

    def start_requests(self):
        if self.product_url:
            yield scrapy.Request(self.product_url, callback=self.parse_product)
        else:
            page = 0
            payload = {"requests": [{"indexName": "shopify_products_families",
                                    "params": f"clickAnalytics=true&distinct=true&"
                                     f"facets=%5B%22facets.Primary%20Category%22%2C%22facets.Availability%22%2C%22facets.Price%22%2C%22onPromotion%22%5D&"
                                     f"filters=%22banner_tags.label%22%3A%20%22On%20Sale%22%20AND%20(price%20%3E%200%20AND%20product_published%20%3D%201%20AND%20availability.displayProduct%20%3D%201)&"
                                     f"highlightPostTag=%3C%2Fais-highlight-0000000000%3E&"
                                     f"highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&"
                                     f"maxValuesPerFacet=100&page={page}&query=&tagFilters="}]}
            yield scrapy.Request(self.algolia_url, body=json.dumps(payload), method='POST', meta={'page': page},
                                 callback=self.parse, headers=self.headers)

    def parse(self, response):
        data = json.loads(response.text)
        try:
            hits = data['results'][0]['hits']
        except:
            hits = []

        if not hits:
            hits = []

        for hit in hits:
            handle = hit.get('handle')
            if handle:
                product_url = urljoin(
                    'https://www.jbhifi.com.au/products/', handle)
                yield scrapy.Request(product_url, callback=self.parse_product)

        if len(hits) > 0:
            page = response.meta.get('page', 0) + 1
            payload = {"requests": [{"indexName": "shopify_products_families",
                                     "params": f"clickAnalytics=true&distinct=true&"
                                               f"facets=%5B%22facets.Primary%20Category%22%2C%22facets.Availability%22%2C%22facets.Price%22%2C%22onPromotion%22%5D&"
                                               f"filters=%22banner_tags.label%22%3A%20%22On%20Sale%22%20AND%20(price%20%3E%200%20AND%20product_published%20%3D%201%20AND%20availability.displayProduct%20%3D%201)&"
                                               f"highlightPostTag=%3C%2Fais-highlight-0000000000%3E&"
                                               f"highlightPreTag=%3Cais-highlight-0000000000%3E&hitsPerPage=36&"
                                               f"maxValuesPerFacet=100&page={page}&query=&tagFilters="}]}
            yield scrapy.Request(self.algolia_url, body=json.dumps(payload), method='POST', meta={'page': page},
                                 callback=self.parse, headers=self.headers)

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
