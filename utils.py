import re
from stemmer import PorterStemmer

def tokenize_and_stem(text):
    stemmer = PorterStemmer()
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [stemmer.stem(token, 0, len(token) - 1) for token in tokens]

def write_to_file(data, file_path):
    with open(file_path, 'w') as f:
        for item in data:
            f.write(f"{item}\n")
