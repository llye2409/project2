import numpy as np
import re
from gensim import corpora, models, similarities
from Ogani.lib.model import irrelevant_words, stop_words


def removeStopwords(text, stop_words):
    """
    Hàm loại bỏ stopwords
    Tham số:
    - text: Đoạn văn bản cần xử lý
    - stop_words: list stopwords
    
    Kết quả:
    - Trả về mô hình content-based filtering đã được xây dựng.
    """
    
    # Chuyển text về lower case
    text = text.lower()
    texts = [text for word in text if word not in stop_words]
    
    # Nối các từ lại thành văn bản
    text_clean = ' '.join(texts)
    
    return text_clean 


def remove_short_words(lst_words):

    # Duyệt qua từng từ và giữ lại các từ có len >= 2
    cleaned_words = []
    for word in lst_words:
        if len(word) >= 2:
            cleaned_words.append(word)

    # Kết hợp các từ lại thành một văn bản mới
    cleaned_text = ' '.join(cleaned_words)

    return cleaned_text


def clean_text_for_search(text, irrelevant_words):
    irrelevant_words_local = irrelevant_words

    text_clean = str(text).lower()
    text_clean = re.sub(r"[0-9]+", '', text)
    text_clean = re.sub(r"'', ' ', ',', '.', '...', '-',':', ';', '?', '%', '(', ')', '+', '/', 'g', 'ml'", '', text)
       
    # Loại bỏ các từ không liên quan đến mô tả sản phẩm
    lst_text_clean = text_clean.split()
    lst_new_text_clean = []
    for t in lst_text_clean:
        if t not in irrelevant_words_local:
            lst_new_text_clean.append(t) 

    # Loại bỏ word nhỏ hơn 2 ký tự
    text_clean = remove_short_words(lst_new_text_clean)

    return text_clean
    

def build_content_based_model(products_gem_re):
    """
    Hàm xây dựng mô hình content-based filtering.
    
    Tham số:
    - text: danh sách các dữ liệu.
    
    Kết quả:
    - Trả về mô hình content-based filtering đã được xây dựng.
    """
    
    # Xây dựng từ điển và véc-tơ đặc trưng cho mỗi văn bản
    dictionary = corpora.Dictionary(products_gem_re)
    corpus = [dictionary.doc2bow(text) for text in products_gem_re]
    
    # Xây dựng mô hình TF-IDF
    tfidf = models.TfidfModel(corpus)
    
    # Trả về mô hình content-based filtering
    index_ = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary))
    return index_, dictionary, tfidf


def recommend_related_products(index_, tfidf, dictionary, products, product_id, num_recommendations=8):
    """
    Hàm đề xuất sản phẩm dựa trên một sản phẩm truy vấn.
    
    Tham số:
    - index: mô hình content-based filtering đã được xây dựng.
    - dictionary: từ điển của dữ liệu.
    - tfidf: mô hình TF-IDF của dữ liệu.
    - products: dataframe chứa thông tin của các sản phẩm.
    - product_id: ID của sản phẩm truy vấn.
    - num_recommendations: số lượng sản phẩm được đề xuất.
    
    Kết quả:
    - Trả về một list chứa các dictionary, mỗi dictionary chứa thông tin sản phẩm đề xuất theo mẫu:
        {'product_id': product_id, 
         'product_name': product_name, 
         'price': price,
         'image': image}
        - list được sắp xếp theo thứ tự giảm dần của độ tương tự.
    """

    # Lấy thông tin sản phẩm truy vấn
    query_product = list(filter(lambda product: product['product_id'] == product_id, products))[0]['description_clean']
    query_product = query_product.lower().split()
    query_bow = dictionary.doc2bow(query_product)
    
    # Tính độ tương tự giữa sản phẩm truy vấn và các sản phẩm khác
    sim = index_[tfidf[query_bow]]
    
    # Sắp xếp giá trị độ tương tự theo thứ tự giảm dần
    sim_sorted = sorted(enumerate(sim), key=lambda x: x[1], reverse=True)
    
    # Lấy ra các sản phẩm đề xuất (loại bỏ sản phẩm truy vấn)
    remmendations_products = [i for i, s in sim_sorted[1:num_recommendations+1]]
    
    # Lấy thông tin của các sản phẩm đề xuất
    recommended_products_info = []
    for i in remmendations_products:
        product_info = products[i]
        recommended_products_info.append({
            'product_id': product_info['product_id'], 
            'product_name': product_info['product_name'], 
            'price': product_info['price'],
            'image': product_info['image']
        })
    
    return recommended_products_info



def recommend_products_for_search(text, index_, dictionary, tfidf, products, stop_words=stop_words, irrelevant_words=irrelevant_words, num_products=5):
    """
    Hàm tìm kiếm và đề xuất các sản phẩm tương tự với văn bản đầu vào.
    
    Tham số:
    - text: Văn bản đầu vào cần tìm kiếm.
    - index: Mô hình content-based filtering đã được xây dựng.
    - dictionary: Từ điển của mô hình.
    - tfidf: Mô hình TF-IDF của mô hình.
    - stop_words: Danh sách stopword
    - irrelevant_words: Danh sách word không liên quan do người dùng định nghĩa
    - products: Danh sách sản phẩm.
    - num_products: Số lượng sản phẩm đề xuất (mặc định là 5).
    
    Kết quả:
    - Trả về danh sách các sản phẩm được đề xuất dưới dạng đối tượng JSON.
    """
    
    # Xử lý văn bản đầu vào
    text_clean = clean_text_for_search(text, irrelevant_words)
    text_clean = removeStopwords(text_clean, stop_words)
    text_tokens = text_clean.split()
    
    # chuyển đổi văn bản thành bag-of-words
    text_bow = dictionary.doc2bow(text_tokens)
    text_tfidf = tfidf[text_bow]
    
    # Tính toán độ tương tự
    similarities = index_[text_tfidf]
    
    # Sắp xếp các sản phẩm theo độ tương tự giảm dần
    sorted_indices = np.argsort(similarities)[::-1]
    
    # Đề xuất các sản phẩm tương tự
    recommended_products = []
    for i in sorted_indices:
        product = products[i]
        product_id = product['product_id']      
        product_name = product['product_name']
        description = product['description']
        price = product['price']
        image = product['image']
        recommended_products.append({'product_id': product_id, 
                                     'product_name': product_name, 
#                                      'description': description,
                                     'price': price,
                                     'image': image})
        if len(recommended_products) == num_products:
            break

    
    return recommended_products