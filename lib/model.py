import pickle

# load the model using pickle
with open('Ogani/data/content_based_model.pkl', 'rb') as f:
    index_, dictionary, tfidf = pickle.load(f)

# Load stop words
STOP_WORD_FILE = 'Ogani/data/vietnamese-stopwords.txt'
with open(STOP_WORD_FILE, 'r', encoding='utf-8') as file:
    stop_words = file.read()
stop_words = stop_words.split('\n')

# Load irrelevant words
irrelevant_file = 'Ogani/data/irrelevant.txt'
with open(irrelevant_file, 'r', encoding='utf-8') as file:
    irrelevant_word = file.read()
irrelevant_words = irrelevant_word.split('\n')