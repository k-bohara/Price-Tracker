import scrapy
from scrapy import Request
from ..items import ProductItem
import json
from ..utils import get_float_or_none, get_int_or_none


class WatchdirectSpider(scrapy.Spider):
    name = "thegoodguys_product"
    allowed_domains = ["thegoodguys.com.au"]

    start_urls = ["https://www.thegoodguys.com.au/deals"]

    def parse(self, response):
        for url in response.css('div.deals_top-deals-slider__tile a::attr(href)').extract():
            yield scrapy.Request(response.urljoin(url), callback=self.parse_cat)

    def parse_cat(self, response):
        products = response.css('div.product-tile-imagewrap')
        for product in products:
            product_url = product.css(
                'a.disp-block::attr(href)').get()
            yield Request(product_url, callback=self.parse_product)

        next_page = response.css(
            'a#WC_SearchBasedNavigationResults_pagination_link_right_categoryResults::attr(href)').get()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse_cat)

    def parse_product(self, response):
        data = response.css(
            'script[type="application/ld+json"]::text').getall()
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
