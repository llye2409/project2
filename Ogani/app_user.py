from Ogani import app, products, users
from Ogani.lib.mylib import *
from Ogani.lib.model import  index_, dictionary, tfidf
from Ogani.lib.NLP import *
from flask import request, render_template, Markup, session, redirect, jsonify


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    
    str_result = ''
    products_recomend_for_user = []
    
    # Kiểm tra nếu đã đăng nhập
    if session.get('session_user') is not None:
        return redirect(url_for('shop'))
    
    # Nếu người dùng submit form đăng nhập
    if request.form.get('user_id'):
        user_id = int(request.form.get('user_id'))
        user = find_user_id(user_id, users)
        
        # Kiểm tra thông tin đăng nhập
        if user is not None:
            
            # Tạo session user
            session['session_user'] = user
            return redirect(url_for('shop'))

        else:
            str_result = "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin."
 
    return render_template('login.html', Str_result=str_result, SP = products_recomend_for_user)


@app.route('/user_logout', methods=['GET', 'POST'])
def user_logout():
    session.pop('session_user', None)
    return redirect(url_for('shop'))

@app.route('/api/recommend_for_user/<int:user_id>')
def recommend_products_by_user_id(user_id):
    
    # Load danh sách product_id gợi ý theo user_id
    user_data = read_json_file(path_user_json)
    user_id = session['session_user']['user_id']
    product_ids = get_top_products(user_id, user_data)

    # Tạo danh sách sản phẩm gợi ý theo user_id
    products_recomend_for_user = search_products_by_id(product_ids, products)

    # Trả về danh sách sản phẩm tương tự dưới dạng JSON
    return jsonify(products_recomend_for_user)



@app.route('/recommend-for-users', methods=['GET', 'POST'])
def recommend_for_user():
    
    products_found = ''
    
    # Kiểm tra nếu đã đăng nhập
    if session.get('session_user') is not None:
        # Load danh sách product_id gợi ý theo user_id
        user_data = load_user_data()
        user_id = session['session_user']['user_id']
        product_ids = get_top_products(user_id, user_data)

        # Tạo danh sách sản phẩm gợi ý theo user_id
        products_recomend_for_user = search_products_by_id(product_ids, products)
        products_found = len(products_recomend_for_user)
        
    else:
        return redirect(url_for('user_login'))

    return render_template('recomend_for_user.html', Products_recomend_for_user = products_recomend_for_user,
                           Products_found = products_found)

