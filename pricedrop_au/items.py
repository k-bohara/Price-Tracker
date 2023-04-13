import scrapy


class ProductItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    mark_price = scrapy.Field()
    sale_price = scrapy.Field()
    sku = scrapy.Field()
    description = scrapy.Field()
    review_count = scrapy.Field()
    average_rating = scrapy.Field()
    main_image = scrapy.Field()
    images = scrapy.Field()
    source = scrapy.Field()  # Amazon, JB-Hifi
    in_stock = scrapy.Field()  # True or False
    scraped_timestamp = scrapy.Field()  # when it was last scraped
