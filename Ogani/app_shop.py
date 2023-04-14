from Ogani import app, products
from Ogani.lib.mylib import *
from Ogani.lib.model import  index_, dictionary, tfidf
from Ogani.lib.NLP import *
from flask import request, render_template, Markup, jsonify, session
import random


@app.route('/')
def index():

    # lấy ngẫu nhiên 8 feature product
    feature_products = random.sample(products, 8)

    # Hiển thị sản phẩm gợi ý theo user
    products_recomend_for_user = []
    # Kiểm tra nếu đã đăng nhập
    if session.get('session_user') is not None:
        # Load danh sách product_id gợi ý theo user_id
        user_data = load_user_data()
        user_id = session['session_user']['user_id']
        product_ids = get_top_products(user_id, user_data)

        # Tạo danh sách sản phẩm gợi ý theo user_id
        products_recomend_for_user = search_products_by_id(product_ids, products)
        # Tạo html sản phẩm gợi ý cho user


    return render_template('index.html', Feature_Products = feature_products, 
                           Products_recomend_for_user = products_recomend_for_user)


@app.route('/search', methods=['GET', 'POST'])
def search():
    
    result_query = ''
    # Đọc danh sách category
    categories = read_json_file(path_categories)  #list
    
    # Đề xuất sản phẩm dựa trên tìm kiếm
    query = request.args.get('query')
    recommended_products_search = recommend_products_for_search(query, index_, 
                                                         dictionary, 
                                                         tfidf, products, 
                                                         stop_words=stop_words, 
                                                         irrelevant_words=irrelevant_words, 
                                                         num_products=100)
    # Hiện thị kết quả
    num_result = len(recommended_products_search)
    if num_result >=1:
        result_query = f'Tìm thấy {num_result} sản phẩm liên quan với tìm kiếm "<em>{query}</em>"'

    else:
        result_query = 'Không tìm thấy thấy kết quả'

    # Tính toán số lượng sản phẩm và số trang
    page, pagination = generate_pagination(recommended_products_search, PER_PAGE)
    # Lấy danh sách sản phẩm cho trang hiện tại
    products_on_page = get_products(page, recommended_products_search)

    return render_template('search_results.html', Recommend_products=products_on_page, 
                           Result_query = Markup(result_query),
                           Products_found=num_result,
                           Categories = categories,
                           pagination=pagination)


@app.route('/shop', methods=['GET', 'POST'])
def shop():

    # Thống kê số lượng sản phẩm
    products_found = len(products)

    # Đọc danh sách category
    categories = read_json_file(path_categories)  #list

    # Tính toán số lượng sản phẩm và số trang
    page, pagination = generate_pagination(products, PER_PAGE)
    # Lấy danh sách sản phẩm cho trang hiện tại
    products_on_page = get_products(page, products)


    return render_template('shop.html', products=products_on_page, 
                           pagination=pagination, 
                           Categories = categories, 
                           Products_found=products_found)

@app.route('/san-pham/<int:product_id>', methods=['GET', 'POST'])
def product_deltail(product_id):
    product_html = ''

    # Lấy thông tin sản phẩm
    product = get_product_by_id(products, product_id)
    
    if product is not None:

        # Tạo html chi tiết sản phẩm
        product_html = create_product_detail_html(product)

    else:
        product_html = '<div>Không tìm thấy sản phẩm. Vui lòng thử lại hoặc tìm sản phẩm khác.</div>'
            
    return render_template('shop-detail.html', Product_html = Markup(product_html))


@app.route('/api/recommend_products/<int:product_id>')
def recommend_products_by_id(product_id):
    # Tải danh sách sản phẩm tương tự
    related_products = recommend_related_products(index_, tfidf, dictionary, products, product_id, num_recommendations=12)

    # Trả về danh sách sản phẩm tương tự dưới dạng JSON
    return jsonify(related_products)


@app.route('/category/<category_name>', methods=['GET', 'POST'])
def category_product(category_name):
    # Đọc danh sách category
    categories = read_json_file(path_categories)

    # Lọc sản phẩm theo category
    filtered_products = [p for p in products if p['sub_category'] == category_name]
    # Thống kê số lượng sản phẩm
    num_result = len(filtered_products)

    # Tính toán số lượng sản phẩm và số trang
    page, pagination = generate_pagination(filtered_products, PER_PAGE)
    # Lấy danh sách sản phẩm cho trang hiện tại
    products_on_page = get_products_in_categories(page, category_name, filtered_products)

    # Truyền danh sách sản phẩm và phân trang vào template
    return render_template('categories.html', Categories=categories, 
                           Category_products=products_on_page, 
                           pagination=pagination, 
                           Products_found=num_result)
