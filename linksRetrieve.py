# -*- coding: utf-8 -*-
"""GreatCode.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1od-k9xZ8btlt8ewfIVQkatx_bxrsvrbn
"""

!pip install playwright
!playwright install
!pip install nest_asyncio

import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv
from playwright.async_api import Page

nest_asyncio.apply()

NUM_LINKS_TO_RETRIEVE = 4000

async def click_load_more_if_needed(page: Page, last_movie_count: int) -> bool:
    try:
        load_more_button = await page.query_selector('button[data-qa="dlp-load-more-button"]')

        if load_more_button:
            await load_more_button.click()
            await page.wait_for_timeout(5000)  # Wait for content to load

            updated_movie_count = len(await page.query_selector_all('a[href*="/m/"]'))  # Adjust selector if needed

            return updated_movie_count > last_movie_count
        else:
            print("No 'Load More' button found.")
            return False
    except Exception as e:
        print(f"Error clicking 'Load More': {e}")
        return False

def extract_movie_links(page_html):
    try:
        soup = BeautifulSoup(page_html, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '/m/' in href:
                full_url = 'https://www.rottentomatoes.com' + href
                links.add(full_url)
        return links
    except Exception as e:
        print(f"Error extracting movie links: {e}")
        return set()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        home_url = 'https://www.rottentomatoes.com/browse/movies_at_home/'
        db = set()

        print(f"Processing home movies link: {home_url}")

        retries = 3
        while retries > 0:
            try:
                await page.goto(home_url, wait_until='domcontentloaded', timeout=180000)

                last_movie_count = len(await page.query_selector_all('a[href*="/m/"]'))

                while len(db) < NUM_LINKS_TO_RETRIEVE:
                    movie_links = extract_movie_links(await page.content())
                    db.update(movie_links)

                    if not await click_load_more_if_needed(page, last_movie_count):
                        break

                    last_movie_count = len(await page.query_selector_all('a[href*="/m/"]'))

                with open('movie_links.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Movie Link'])
                    for link in list(db)[:NUM_LINKS_TO_RETRIEVE]:
                        writer.writerow([link])

                print(f"Total movie links fetched: {len(db)}")
                break

            except Exception as e:
                print(f"Error during page processing: {e}")
                retries -= 1
                if retries > 0:
                    print(f"Retrying... {retries} attempts left.")
                await page.close()
                page = await browser.new_page()

        await browser.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())