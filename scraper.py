from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def scrape_page_text(url, max_items=200):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(2)  # wait for page to render
    soup = BeautifulSoup(driver.page_source, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "untitled"
    driver.quit()

    tags = ["button", "span", "a", "div", "p", "li"]
    text_blocks = []

    for tag in tags:
        for el in soup.find_all(tag):
            if len(text_blocks) >= max_items:
                break  # stop collecting after N items
            text = el.get_text(strip=True)
            if text and len(text) > 5:
                text_blocks.append(text)

        if len(text_blocks) >= max_items:
            break  # optional: stop tag loop too

    # Format as a single string with newlines between blocks
    formatted_text = f"Title: {title}\n\n"
    formatted_text += "\n".join(f"- {block}" for block in text_blocks)
    return formatted_text