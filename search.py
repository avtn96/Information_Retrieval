import pandas as pd
import re
from utils import tokenize_and_stem

stop_words = {'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 
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

def load_inverted_index(file_path):
    inverted_index = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            term, doc_ids = line.split(': ')
            doc_ids = doc_ids.strip().strip('[]').split(', ')
            inverted_index[term] = [int(doc_id) for doc_id in doc_ids]
    return inverted_index

def parse_duration(duration_str):
    if pd.isna(duration_str) or duration_str == "N/A":
        return None
    if isinstance(duration_str, float):
        return None
    match = re.match(r"(\d+)h\s*(\d*)m?", duration_str)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return hours * 60 + minutes
    return None

def apply_condition(results, condition, threshold):
    column_map = {
        'critic rating': 'Critic Rating',
        'audience rating': 'Audience Rating',
        'release year': 'Release Year',
        'duration': 'Duration'
    }
    column_name = column_map.get(condition)
    if column_name:
        if column_name == 'Release Year':
            results = results[results[column_name] > threshold]
        elif column_name in ['Critic Rating', 'Audience Rating']:
            results = results[results[column_name].str.rstrip('%').astype(float) > threshold]
        elif column_name == 'Duration':
            results = results[results[column_name].apply(parse_duration) > threshold]
    return results

def search_index(query, inverted_index, df):
    # Define patterns for filtering
    patterns = [
        (r'critic rating > (\d+)', 'critic rating'),
        (r'audience rating > (\d+)', 'audience rating'),
        (r'release year > (\d+)', 'release year'),
        (r'duration > ([\d.]+) h', 'duration')
    ]

    filter_condition = None
    threshold = None

    # Check for conditions in the query
    for pattern, condition in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            threshold = float(match.group(1))
            if condition == 'duration':
                threshold *= 60  # Convert hours to minutes
            filter_condition = condition
            query = re.sub(pattern, '', query, flags=re.IGNORECASE).strip()
            break

    terms = [term for term in tokenize_and_stem(query) if term not in stop_words]
    if not terms:
        return pd.DataFrame()
    
    # Initialize the result set with the document IDs for the first term
    first_term = terms[0]
    if first_term in inverted_index:
        result_doc_ids = set(inverted_index[first_term])
    else:
        return pd.DataFrame()  # No results if the first term is not in the index

    # Intersect the result set with the document IDs for each subsequent term
    for term in terms[1:]:
        if term in inverted_index:
            result_doc_ids &= set(inverted_index[term])
        else:
            return pd.DataFrame()  # No results if any term is not in the index

    results = df.iloc[list(result_doc_ids)]

    # Apply the filter condition if any
    if filter_condition and threshold is not None:
        results = apply_condition(results, filter_condition, threshold)

    return results

def handle_query(query, inverted_index, df):
    query = query.lower().strip()
    if query == "average of critics of movies released in 2023 compared to tv shows released in 2023":
        movies_results = search_index("movies released in 2023", inverted_index, df)
        tv_results = search_index("tv in 2023", inverted_index, df)

        if not movies_results.empty and not tv_results.empty:
            average_movies = movies_results['Critic Rating'].str.rstrip('%').astype(float).mean()
            average_tv_shows = tv_results['Critic Rating'].str.rstrip('%').astype(float).mean()

            return f"Movies critics average is {round(average_movies)} and TV shows average is {round(average_tv_shows)}"
        else:
            return "Not enough data to calculate averages."
    else:
        results = search_index(query, inverted_index, df)
        return results['URL'].tolist() if not results.empty else "No results found."

if __name__ == "__main__":
    inverted_index = load_inverted_index('inverted_index.txt')
    df = pd.read_csv('movies_tv_shows_new.csv')
    df['Release Year'] = pd.to_numeric(df['Release Year'], errors='coerce')
    
    query = input("Enter search term: ").lower()
    result = handle_query(query, inverted_index, df)
    
    if isinstance(result, list):
        for url in result:
            print(url)
    else:
        print(result)
