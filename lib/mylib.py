import csv
from flask import url_for, request
import json
from flask_paginate import Pagination, get_page_parameter

PER_PAGE = 12   # Số sản phẩm trên mỗi trang
user_data = None
path_categories = 'Ogani/data/categories.json'
path_user_json = 'Ogani/data/users.json'

def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def get_top_products(user_id, user_data):
    for user in user_data:
        if user['user_id'] == user_id:
            return user['top_products']
    return []


def read_products_from_csv(file_path):
    products = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader) # Bỏ qua dòng tiêu đề nếu có
        for row in reader:
            try:
                price = float(row[4])
            except ValueError:
                price = 0
                
            try:
                rating = float(row[5])
            except ValueError:
                rating = 0
                
            product = {
                'product_id': int(row[0]),
                'product_name': row[1],
                'category': row[2],
                'sub_category': row[3],
                'price': row[4],
                'rating': row[5],
                'description': row[6],
                'description_clean': row[7],
                'image': row[8]
            }
            products.append(product)
    return products

def get_products(page, products):
    """
    Hàm lấy số sản phẩm trên mỗi trang
    Tham số:
    page: số trang
    products: List danh sách sản phẩm, mỗi sản phẩm là dictionary
    kết quả: Trả về danh sách sản phẩm tại trang page
    """
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    return products[start:end]

def get_products_in_categories(page, category_name, products):
    """
    Hàm lấy số phẩm trên mỗi trang từ categories
    Tham số:
    page: số trang
    category_name: tên danh mục
    products: List danh sách sản phẩm, mỗi sản phẩm là dictionary
    kết quả: Trả về danh sách sản phẩm tại trang page
    """
    filtered_products = [p for p in products if p['sub_category'] == category_name]
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    return filtered_products[start:end]

def generate_pagination(products, PER_PAGE = 12):
    """
    Hàm tính toán số lượng sản phẩm và số trang từ Flask-Paginate dựa trên danh sách sản phẩm
    Tham số:
    products: Danh sách sản phẩm
    PER_PAGE: số sản phẩm trên mỗi trang, PER_PAGE là biến toàn cục
    Kết quả: Trả về đối tượng phân trang pagination
    """
    # Tính toán số lượng sản phẩm và số trang
    total = len(products)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=total, per_page=PER_PAGE, css_framework='bootstrap')

    return page, pagination

def get_product_deltail(products, product_id):
    """
    Hàm lấy thông tin sản phẩm từ danh sách sản phẩm
    
    Tham sô:
    products: Danh sách sản phẩm, mỗi sản phẩm là dictionary
    product_id: id sản phẩm
    """ 
    product = list(filter(lambda product: product['product_id'] == product_id, products))
    product = product[0] if len(product) == 1 else None
    return product

def get_product_by_id(products, product_id):
    for product in products:
        if product['product_id'] == product_id:
            return product
    return None

def search_products_by_id(product_ids, products):
    return [product for product in products if product['product_id'] in product_ids]

def read_user_from_csv(users_path):
    users = []
    with open(users_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader) # Bỏ qua dòng tiêu đề nếu có
        for row in reader:
            
            user = {
                'user_id': int(row[1]),
                'user': row[2]
            }
            users.append(user)
    return users


def login_for_user(users, user_name):
    pass

def find_user_id(user_id, user_list):
    for user in user_list:
        if user['user_id'] == user_id:
            return user
    return None

def load_user_data():
    global user_data
    
    # Nếu user data đã được load
    if  user_data is not None:
        return user_data
    
    # Chưa có thì load user_data
    user_data = read_json_file(path_user_json)
    
    return user_data


def generate_product_list_html(products):
    product_list_html = ''
    for product in products:
        product_html = f'''
            <div class="product">
                <h2>{product['product_id']} - {product['product_name']}</h2>
                <p>Giá: {product['price']}</p>
                <p>Rating: {product['rating']}</p>
            </div>
        '''
        product_list_html += product_html
    return product_list_html

def create_product_detail_html(product):

    image_src = url_for('static', filename='img/products/' + product['image'] + '/1.jpg')
    html = f"""
        <div class="col-lg-6 col-md-6">
            <div class="product__details__pic">
                <div class="product__details__pic__item">
                    <img class="product__details__pic__item--large" src="{image_src}">
                </div>
            </div>
        </div>
        <div class="col-lg-6 col-md-6">
            <div class="product__details__text">
                <h3>{product['product_name']}</h3>    
                <div class="product-rating">
                    <span class="fa fa-star checked"> Review: </span>{product['rating']}</span>
                </div>
                <div class="product__details__price">{product['price']} đ</div>
                <p>{product['description'][:200] + "..."}</p>
                <div class="product__details__quantity">
                    <div class="quantity">
                        <div class="pro-qty">
                            <input type="text" value="1">
                        </div>
                    </div>
                </div>
                <a href="#" class="primary-btn">ADD TO CARD</a>
                <a href="#" class="heart-icon"><span class="icon_heart_alt"></span></a>
                <ul><li><b>category:</b> <span>{product['sub_category']}</span></li></ul>
            </div>
        </div>
        <div class="col-lg-12">
            <div class="product__details__tab">
                <ul class="nav nav-tabs" role="tablist">
                    <li class="nav-item">
                        <a class="nav-link active" data-toggle="tab" href="#tabs-1" role="tab"
                            aria-selected="true">Description</a>
                    </li>
                </ul>
                <div class="tab-content">
                    <div class="tab-pane active" id="tabs-1" role="tabpanel">
                        <div class="product__details__tab__desc"></div>
                        {product['description']}
                    </div>
                </div>
            </div>
        </div>
    """
    return html
