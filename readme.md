## Price Tracker By Kaman

#### .env setup

Create a copy of .env.example to .env and update according to your database setup

    $ cp .env.example .env

## Install requirements

    (venv) $ pip install -r requirements.txt

## Clone project

    $ git clone https://github.com/k-bohara/Price-Tracker.git

## Database

Log in to an interactive Postgres session:

    $ sudo -iu postgres psql;

Creating postgres database and user:
$ CREATE DATABASE price_tracker;

## create a database user for the project and provide secure password:

    $ CREATE USER username WITH PASSWORD 'your_password';

## provide database access to the user:

    $ GRANT ALL PRIVILEGES ON DATABASE database_name TO user_name;

## To verify if the database is created successfully and get the list of all the databases:

    $ \l

## to exit:

$ \q

## to connect the database:

    $ \c database_name
    or
    $ psql -U user databse_name

Grant permission to schema public:

    $ GRANT USAGE ON SCHEMA public TO user_name;

Create table product:

    $ create table product (
        title varchar(512),
        mark_price float8,
        sale_price float8,
        sku varchar(128),
        description text,
        review_count int,
        average_rating float8,
        main_image varchar(512),
        images text,
        source varchar(128),
        in_stock boolean,
        scraped_timestamp timestamp
    );

To check if table is created:

$ \dt

## connect app to the database:

    $ hostname = 'hostname'
        username = 'username'
        password = 'your password'
        database = 'price_tracker'

        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

# inserting data into product:

    $ self.cur.execute('''
            INSERT INTO product (title, mark_price, sale_price, sku, description, review_count, average_rating, main_image, images, source, in_stock, scraped_timestamp)  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (item['title'], item['mark_price'], item['sale_price'], item['sku'], item['description'], item['review_count'], item['average_rating'], item['main_image'], images, item['source'], item['in_stock'], item['scraped_timestamp']));

## runing spider code to scrape data

    $ scrapy crawl amazon_product -a product_url="<product_url>"

## to check the program version:

    $ pip3 freeze | grep -i scrapy

## to install particular version:

    $ pip3 install pytz==2021.1
