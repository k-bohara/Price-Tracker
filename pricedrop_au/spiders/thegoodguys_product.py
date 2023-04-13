import scrapy
from scrapy import Request
from ..items import ProductItem
import json
from ..utils import get_float_or_none, get_int_or_none


class WatchdirectSpider(scrapy.Spider):
    name = "thegoodguys_product"
    allowed_domains = ["thegoodguys.com.au"]
    start_urls = ["http://thegoodguys.com.au/"]

    def __init__(self, product_url, **kwargs):
        super().__init__(**kwargs)
        self.product_url = product_url

    def start_requests(self):
        yield Request(url=self.product_url)

    def parse(self, response):
        data = response.css('script[type="application/ld+json"]::text').getall()
        data = json.loads(data[1])
        item = ProductItem()
        item['title'] = data['name']
        item['source'] = 'TheGoodGuys'
        item['url'] = response.url
        item['description'] = data['description']
        item['sku'] = data['sku']
        item['mark_price'] = None
        item['sale_price'] = data['offers'][0]['price']
        item['images'] = [response.urljoin(img) for img in
                          response.css('img.product-image-main::attr(data-lazy)').getall()]
        item['main_image'] = response.urljoin(data['image'][0])
        item['in_stock'] = None
        try:
            item['review_count'] = data['aggregateRating']['reviewCount']
        except:
            item['review_count'] = None

        try:
            item['average_rating'] = data['aggregateRating']['ratingValue']
        except:
            item['average_rating'] = None
        return item
