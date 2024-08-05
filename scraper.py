import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd
import re

async def scrape_movie_data(url):
    print(f"Scraping data from: {url}")
    browser = await launch(headless=True, executablePath='C:/Program Files/Google/Chrome/Application/chrome.exe')  # Update with the path to your Chrome
    page = await browser.newPage()
    await page.goto(url)
    await page.waitForSelector('h1.unset')
    content = await page.content()
    await browser.close()

    soup = BeautifulSoup(content, 'html.parser')

    title_tag = soup.find('h1', class_='unset')
    genre_tag = soup.find('rt-text', slot='genre')
    release_date_tag = soup.find('rt-text', slot='releaseDate')
    description_tag = soup.find('rt-text', slot='content')
    duration_tag = soup.find('rt-text', slot='duration')
    critic_score_tag = soup.find('rt-text', slot='criticsScore')
    audience_score_tag = soup.find('rt-text', slot='audienceScore')

    title = title_tag.text.strip() if title_tag else 'N/A'
    genre = genre_tag.text.strip() if genre_tag else 'N/A'
    release_date = release_date_tag.text.strip() if release_date_tag else 'N/A'
    release_year_match = re.search(r'\d{4}', release_date)
    release_year = release_year_match.group(0) if release_year_match else 'N/A'
    description = description_tag.text.strip() if description_tag else 'N/A'
    duration = duration_tag.text.strip() if duration_tag else 'N/A'
    critic_rating = critic_score_tag.text.strip() if critic_score_tag else 'N/A'
    audience_rating = audience_score_tag.text.strip() if audience_score_tag else 'N/A'

    what_to_know_tag = soup.find('h2', id='what-to-know-label')
    consensus_text = what_to_know_tag.find_next('div', class_='content').find('div', class_='consensus').text.strip() if what_to_know_tag else 'N/A'

    tags = set()
    for tag_element in soup.find_all('where-to-watch-bubble'):
        tag = tag_element.get('image')
        if tag:
            tags.add(tag)

    type_ = 'TV Show' if '/tv/' in url else 'Movie'

    movie_data = {
        'Title': title,
        'Genre': genre,
        'Release Date': release_date,
        'Release Year': release_year,
        'Description': description,
        'Duration': duration,
        'Critic Rating': critic_rating,
        'Audience Rating': audience_rating,
        'Consensus Text': consensus_text,
        'Tags': tags,
        'URL': url,
        'Type': type_
    }

    return movie_data

async def main():
    with open('movie_links.txt', 'r') as f:
        links = f.read().splitlines()

    data = []
    all_tags = set()

    for idx, link in enumerate(links, start=1):
        try:
            print(f"Scraping {idx}/{len(links)}: {link}")
            movie_data = await scrape_movie_data(link)
            data.append(movie_data)
            all_tags.update(movie_data['Tags'])
        except Exception as e:
            print(f"Error scraping {link}: {e}")

    df = pd.DataFrame(data)
    
    # Add columns for each tag
    for tag in all_tags:
        df[tag] = df['Tags'].apply(lambda x: 'Yes' if tag in x else 'No')
    
    df.drop(columns=['Tags'], inplace=True)
    df.to_csv('movies_tv_shows_new.csv', index=False)  # Changed the file name
    print("Data saved to movies_tv_shows_new.csv")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
