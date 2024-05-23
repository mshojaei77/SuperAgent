from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time
from tenacity import retry, wait_random_exponential, stop_after_attempt

class WebReader:
    def __init__(self, parser='html.parser', headers=None, proxy=None, timeout=10, cache_expiry=3600, max_cache_size=1000, max_workers=None):
        self.parser = parser
        self.proxy = proxy
        self.timeout = timeout
        self.cache_expiry = cache_expiry
        self.max_cache_size = max_cache_size
        self.max_workers = max_workers
        self.cache = {}
        if headers:
            self.headers = headers
        else:
            self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "DNT": "1",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1"
            }


    def fetch_html(self, url):
        if url in self.cache and self.cache[url]['expiry'] > time.time():
            return self.cache[url]['content']
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_extra_http_headers(self.headers)
            page.goto(url, timeout=self.timeout * 1000)
            html_content = page.content()
            browser.close()
            self.cache[url] = {'content': html_content, 'expiry': time.time() + self.cache_expiry}
            return html_content

    def scrape_and_search(self, url, search_query, min_result_length=50):
        html_content = self.fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, self.parser)
            matching_tags = soup.find_all(string=re.compile(f'\\b{search_query}\\b', re.I))
            results = []
            for tag in matching_tags:
                parent_tag = tag.parent
                if parent_tag:
                    text = parent_tag.get_text(strip=True)
                    if len(text) >= min_result_length:
                        results.append(text)
            return results
        return []

    def scrape_tag(self, url, tag, attrs=None):
        html_content = self.fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, self.parser)
            elements = soup.find_all(tag, attrs=attrs)
            return [element.text.strip() for element in elements if element.text.strip()]
        return []

    def scrape_all(self, url):
        html_content = self.fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, self.parser)
            return [element.text.strip() for element in soup.find_all()]
        return []

           
    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def scrape_texts(self, url, min_result_length=40):
        html_content = self.fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, self.parser)
            texts = [element.string for element in soup.find_all(string=True) if element.parent.name not in ['style', 'script', 'head', 'title', 'meta', '[document]']]
            cleaned_texts = [re.sub(r'\s+', ' ', text.strip()) for text in texts if text and len(text.strip()) >= min_result_length]
            return cleaned_texts
        return []

    def scrape_links(self, url):
        html_content = self.fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, self.parser)
            return [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]

    def scrape_post(self, url):
        html_content = self.fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, self.parser)
            return [element.text.strip() for element in soup.find_all(['p', 'article', 'span'])]
        return []

if __name__ == "__main__":
    scraper = WebReader(
        parser='html.parser',
        headers=None,
        proxy=None,
        timeout=10,
        cache_expiry=3600,
        max_cache_size=1000,
        max_workers=None
    )

    url = "https://en.wikipedia.org/wiki/OpenAI"
    search_query = 'sam altman'
    min_result_length=100

    clean_texts = scraper.scrape_texts(url, min_result_length)
    search_in_url = scraper.scrape_and_search(url, search_query, min_result_length)
    posts = scraper.scrape_post(url)
    custom_tag = scraper.scrape_tag(url=url, tag='p')
    all_elements = scraper.scrape_all(url)
    links_list = scraper.scrape_links(url)
    print(" ".join(clean_texts))

    [print(link) for link in links_list]