# crawler.py

import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from scraper import scrape_page_text

def is_valid_link(base, link):
    return urlparse(link).netloc == "" or urlparse(link).netloc == urlparse(base).netloc

def crawl_site(base_url, max_pages=1):
    visited = set()
    to_visit = [base_url]
    results = []

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue

        print(f"[Crawling] {current_url}")
        visited.add(current_url)

        try:
            res = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
        except:
            continue

        # Get internal links
        for a_tag in soup.find_all("a", href=True):
            href = urljoin(current_url, a_tag['href'])
            if is_valid_link(base_url, href) and href not in visited:
                to_visit.append(href)

        # Scrape the current page and format the result
        page_content = scrape_page_text(current_url)
        results.append(f"URL: {current_url}\n{page_content}\n{'='*80}\n")

    return results