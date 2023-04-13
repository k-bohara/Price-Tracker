import scrapy
from scrapy import Request
from ..items import ProductItem
import json
from ..utils import get_float_or_none, get_int_or_none


class WatchdirectSpider(scrapy.Spider):
    name = "watchdirect_product"
    allowed_domains = ["watchdirect.com.au"]
    start_urls = ["http://watchdirect.com.au/"]

    def __init__(self, product_url, **kwargs):
        super().__init__(**kwargs)
        self.product_url = product_url

    def start_requests(self):
        yield Request(url=self.product_url)

    def parse(self, response):
        data = json.loads(response.css(
            'script[type="application/ld+json"]::text').get())
        item = ProductItem()
        item['title'] = data['name']
        item['source'] = 'watchdirect'
        item['url'] = response.url
        item['description'] = data['description']
        item['sku'] = data['sku']
        try:
            item['mark_price'] = response.css(
                'span.ProductMeta__Price.Price--compareAt::text').get().split()[0].replace('$', '')
        except:
            item['marked_price'] = ''
        item['sale_price'] = data['offers'][0]['price']
        item['images'] = response.css(
            'div.Product__SlideItem.Product__SlideItem--image img.Image--lazyLoad::attr(data-original-src)').getall()
        item['main_image'] = data['image']['image']

        in_stock = data['offers'][0]['availability'].split('/')[3]
        if 'instock' in in_stock.lower():
            item['in_stock'] = True
        else:
            item['in_stock'] = False

        try:
            item['review_count'] = data['aggregateRating']['ratingCount']
        except:
            item['review_count'] = None

        try:
            item['average_rating'] = data['aggregateRating']['ratingValue']
        except:
            item['average_rating'] = None
        return item
