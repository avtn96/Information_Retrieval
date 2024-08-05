from prettytable import PrettyTable
import pandas as pd
import csv
from search import load_inverted_index, search_index

def query_academy_award_non_comedy(df):
    results = df[(df['Genre'].str.contains('Drama')) & (df['Critic Score'] == '100')]
    return results

def query_stars_in_multiple_best_picture(df):
    df['Stars'] = df['Description'].apply(lambda x: x.split(', '))
    all_stars = [star for stars in df['Stars'] for star in stars]
    star_counts = pd.Series(all_stars).value_counts()
    top_stars = star_counts[star_counts > 4]
    return df[df['Stars'].apply(lambda x: any(star in x for star in top_stars.index))]

def query_highest_rated_tv_series(df):
    df['Release Date'] = pd.to_datetime(df['Release Date'])
    results = df[(df['Release Date'] < '2004-01-01') & (df['Genre'].str.contains('TV'))]
    results = results.sort_values(by='Critic Score', ascending=False)
    return results

if __name__ == "__main__":
    df = pd.read_csv('movies_tv_shows.csv')

    print("Query 1: Films that won the Academy Award for Best Non-Comedy Film since 2000")
    results = query_academy_award_non_comedy(df)
    print(results)

    print("Query 2: Stars who starred in more than four films that won the Oscar for Best Picture")
    results = query_stars_in_multiple_best_picture(df)
    print(results)

    print("Query 3: Highest rated TV series on IMDb that started airing more than 20 years ago")
    results = query_highest_rated_tv_series(df)
    print(results)
