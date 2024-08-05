def top_terms(inverted_index_file, top_n=15):
    with open(inverted_index_file, 'r', encoding='utf-8') as f:
        inverted_index = {}
        for line in f:
            term, doc_ids = line.split(': ')
            doc_ids = doc_ids.strip().strip('[]').split(', ')
            inverted_index[term] = doc_ids

    # Filter out numeric terms and empty terms
    filtered_index = {term: doc_ids for term, doc_ids in inverted_index.items() if not term.isnumeric() and term.isalpha() and term != 'nan'}

    # Sort terms by the length of their doc_ids list and take the top_n
    sorted_terms = sorted(filtered_index.items(), key=lambda item: len(item[1]), reverse=True)[:top_n]

    return sorted_terms

if __name__ == "__main__":
    top_terms_list = top_terms('inverted_index.txt')
    for term, doc_ids in top_terms_list:
        print(f"{term}: {len(doc_ids)}")
