import pandas as pd
from utils import tokenize_and_stem

stop_words = stop_words = {'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 
                           'an', 'and', 'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because', 
                           'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 
                           'couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn', 
                           "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'few', 'for', 
                           'from', 'further', 'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 
                           'haven', "haven't", 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 
                           'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', "isn't", 'it', 
                           "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 
                           'more', 'most', 'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 
                           'nor', 'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 
                           'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', "shan't", 
                           'she', "she's", 'should', "should've", 'shouldn', "shouldn't", 'so', 'some', 'such', 
                           't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 
                           'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 
                           've', 'very', 'was', 'wasn', "wasn't", 'we', 'were', 'weren', "weren't", 'what', 'when', 'where', 
                           'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 'y', 
                           'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'}

def create_inverted_index(df):
    inverted_index = {}
    
    # Index textual columns
    textual_columns = ['Title', 'Genre', 'Release Date', 'Release Year', 'Description', 'Duration', 
                       'Critic Rating', 'Audience Rating', 'Consensus Text', 'Type']
    
    for idx, row in df.iterrows():
        doc_id = idx
        for column in textual_columns:
            terms = tokenize_and_stem(str(row[column]))
            for term in terms:
                if term not in stop_words:  # Remove stop words
                    if term not in inverted_index:
                        inverted_index[term] = []
                    inverted_index[term].append(doc_id)
    
    # Index streaming service columns
    streaming_services = {
        'netflix': 'netflix',
        'max-us': 'max',
        'fandango': 'fandango',
        'vudu': 'vudu',
        'disney-plus-us': 'disney',
        'paramount-plus-us': 'paramount',
        'peacock': 'peacock',
        'apple-tv-us': 'appletv',
        'apple-tv-plus-us': 'appletvplus',
        'hulu': 'hulu',
        'amazon-prime-video-us': 'amazonprime'
    }
    
    for service_column, term in streaming_services.items():
        for idx, row in df.iterrows():
            if row[service_column] == 'Yes':
                if term not in inverted_index:
                    inverted_index[term] = []
                inverted_index[term].append(idx)
    
    return inverted_index

if __name__ == "__main__":
    df = pd.read_csv('movies_tv_shows_new.csv')
    inverted_index = create_inverted_index(df)
    
    with open('inverted_index.txt', 'w', encoding='utf-8') as f:
        for term, doc_ids in inverted_index.items():
            f.write(f"{term}: {doc_ids}\n")
    
    print("Inverted index created and saved to inverted_index.txt")