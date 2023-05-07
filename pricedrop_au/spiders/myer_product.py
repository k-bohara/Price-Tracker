import json
import scrapy
from scrapy import Request
import html

from ..items import ProductItem


class MyerProductSpider(scrapy.Spider):
    name = 'myer_product'
    allowed_domains = ['myer.com.au', 'bazaarvoice.com']

    start_urls = ["https://www.myer.com.au/c/offers/sale-all"]

    def parse(self, response):
        products = response.css('div[data-automation="product"]')
        for product in products:
            product_url = response.urljoin(product.css(
                'div[data-automation="product"] a::attr(href)').get())
            yield Request(url=product_url, callback=self.parse_product)

        next_link = response.css(
            'li[data-automation="paginateNextPage"] a::attr(href)').get()
        yield scrapy.Request(response.urljoin(next_link), callback=self.parse)

    def parse_product(self, response):
        data = response.css(
            'script[data-automation="seo-product-schema"]::text').get()
        json_data = json.loads(html.unescape(data))

        item = ProductItem()
        item['title'] = json_data.get('name')
        item['url'] = response.url
        item['source'] = 'Myer'
        item['sale_price'] = json_data.get('offers').get('price')
        item['mark_price'] = response.css(
            'h3[data-automation="product-price-was"]::text').get().replace('$', '')
        item['sku'] = json_data.get('sku')
        for image in json_data.get('image'):
            item['images'] = image
        sku = item['sku']
        desc = []
        for li in response.css('li[data-automation="pep-attribute-list-item"]'):
            desc.append(''.join(li.css(' ::text').extract()))
        item['description'] = '\n'.join(desc)

        item['description'] = item['description'] + '\n\n' + '\n'.join(
            response.css('div[data-automation="product-description-description"] ::text').extract())

        feedback_url = f'https://api-online.myer.com.au/v2/product/productsupplemental?products={sku}&itemDetails=true'
        yield Request(url=feedback_url, callback=self.parse_details, meta={'item': item})

    def parse_details(self, response):
        item = response.meta.get('item')
        data = json.loads(response.text)
        product_id = data['productList'][0]['internalId']
        in_stock = data['productList'][0]['stockIndicator']
        if 'instock' in in_stock.lower():
            item['in_stock'] = True
        else:
            item['in_stock'] = False

        rating_review_url = f'https://api.bazaarvoice.com/data/display/0.2alpha/product/summary?PassKey=ca3JzrHhYAFG98Vhal06rzBxGsYnsrGMhTPa43TZTylqM&productid={product_id}&contentType=reviews,questions&reviewDistribution=primaryRating,recommended&rev=0&contentlocale=en_AU,en_US,en_CA,en_GB,en_NO,en_NZ,en_DK,en_HK,en_AE,en_ID,en_IN,en_SG,en_TH,en_IE,en_ZA,en_SA'
        yield Request(rating_review_url, callback=self.parse_feedback, meta={'item': item}, dont_filter=True)

    def parse_feedback(self, response):
        item = response.meta.get('item')
        data = json.loads(response.text)
        item['average_rating'] = data['reviewSummary']['primaryRating']['average']
        item['review_count'] = data['reviewSummary']['numReviews']

        return item
