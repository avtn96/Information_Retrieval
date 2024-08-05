from flask import Flask, request, render_template
import pandas as pd
from search import handle_query, load_inverted_index

app = Flask(__name__)

inverted_index = load_inverted_index('inverted_index.txt')
df = pd.read_csv('movies_tv_shows_new.csv')
df['Release Year'] = pd.to_numeric(df['Release Year'], errors='coerce')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_query():
    query = request.args.get('query')
    page = int(request.args.get('page', 1))
    per_page = 10

    if query:
        result = handle_query(query, inverted_index, df)

        if isinstance(result, str):
            return render_template('index.html', result=result, query=query)
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = result[start:end]

        next_url = f"/search?query={query}&page={page + 1}" if end < len(result) else None
        prev_url = f"/search?query={query}&page={page - 1}" if start > 0 else None

        return render_template('index.html', result=paginated_results, next_url=next_url, prev_url=prev_url, query=query)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
