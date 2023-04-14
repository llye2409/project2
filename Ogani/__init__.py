from flask import Flask
from Ogani.lib.mylib import read_products_from_csv, read_user_from_csv
from werkzeug.routing import BaseConverter
from urllib.parse import quote

# decode url for special character
class UnicodeConverter(BaseConverter):
    def to_python(self, value):
        return value

    def to_url(self, value):
        return quote(value, safe='')

# Define the app
app = Flask(__name__)
app.url_map.converters['unicode'] = UnicodeConverter

# Define the session
app.secret_key = 'User_session'

# Load data products csv
file_path_products = 'Ogani/data/product.csv'
products = read_products_from_csv(file_path_products)

# Load users
users_path = 'Ogani/data/rating.csv'
users = read_user_from_csv(users_path)

import Ogani.app_shop
import Ogani.app_user