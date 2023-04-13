import scrapy
from scrapy import Request
from ..items import ProductItem


class HarveyNormanProductSpider(scrapy.Spider):
    name = 'harveynorman_product'
    allowed_domains = ['harveynorman.com.au']

    def __init__(self, product_url, **kwargs):
        super().__init__(**kwargs)
        self.product_url = product_url

    def start_requests(self):
        yield Request(url=self.product_url, callback=self.parse_product)

    def parse_product(self, response):
        item = ProductItem()
        item['title'] = response.css('span.product-name::text').get()
        item['url'] = response.url
        item['sku'] = response.css('small.product-id::text').get()
        item['source'] = 'HarveyNorman'
        item['sale_price'] = round(
            float(response.css('div#product-view-price::attr(data-price)').get()), 2)
        item['average_rating'] = response.css(
            'dd.bv-rating-ratio::attr(title)').get().split()[0]
        item['review_count'] = response.css(
            'span.bv-rating-label span::text').get('')
        item['description'] = response.css(
            'div.product-short-description.short-description p::text').get('')
        item['main_image'] = response.css(
            'div.carousel-item--image img::attr(src)').get()
        item['images'] = response.css('img::attr(data-image-src)').extract()

        return item
