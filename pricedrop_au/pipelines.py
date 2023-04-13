import os
from datetime import datetime

import psycopg2

import pytz

from .utils import *

from dotenv import load_dotenv

load_dotenv()


class ProcessingPipeline:
    def process_item(self, item, spider):
        for field in ['mark_price', 'sale_price', 'average_rating']:
            if field in item:
                if item[field] is not None:
                    item[field] = get_float_or_none(item[field])

        if 'review_count' in item:
            if item['review_count'] is not None:
                item['review_count'] = get_int_or_none(item['review_count'])

        for field in ['title', 'description']:
            if field in item:
                if item[field] is not None:
                    item[field] = item[field].replace('\xa0', ' ').strip()

        if 'scraped_timestamp' not in item:
            item['scraped_timestamp'] = datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S')

        return item


class PostgresPipeline:
    def __init__(self):
        hostname = os.getenv('hostname')
        username = os.getenv('username')
        password = os.getenv('password')
        database = os.getenv('database')

        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

    def process_item(self, item, spider):
        fields = ['title', 'mark_price', 'sale_price', 'sku', 'description', 'review_count', 'average_rating',
                  'main_image', 'images', 'source', 'in_stock', 'scraped_timestamp']

        for field in fields:
            if field not in item:
                item[field] = None

        images = ' || '.join(item['images'])

        self.cur.execute('''
            INSERT INTO product (title, mark_price, sale_price, sku, description, review_count, average_rating, main_image, images, source, in_stock, scraped_timestamp)  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            item['title'], item['mark_price'], item['sale_price'], item['sku'], item['description'],
            item['review_count'],
            item['average_rating'], item['main_image'], images, item['source'], item['in_stock'],
            item['scraped_timestamp']))

        ## Execute insert of data into database
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
