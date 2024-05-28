import requests
from bs4 import BeautifulSoup
import re
import time
from playwright.sync_api import sync_playwright

class WebReader:
    def __init__(self, headless=False, parser='html.parser', headers=None, proxy=None, timeout=10):
        self.headless = headless
        self.parser = parser
        self.proxy = proxy
        self.timeout = timeout
        self.cache = {}
        self.cache_expiry = 3600  # Correct initialization to float
        self.headers = headers if headers else {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "DNT": "1",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1"
        }

    def fetch_html(self, url):
        if self.headless:
            return self._fetch_html_playwright(url)
        else:
            return self._fetch_html_requests(url)

    def _fetch_html_requests(self, url):
        if url in self.cache and self.cache[url]['expiry'] > time.time():
            return self.cache[url]['content']
        try:
            response = requests.get(url, headers=self.headers, proxies=self.proxy, timeout=self.timeout)
            response.raise_for_status()
            html_content = response.text
            self.cache[url] = {'content': html_content, 'expiry': time.time() + self.cache_expiry}
            return html_content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _fetch_html_playwright(self, url):
        if url in self.cache and self.cache[url]['expiry'] > time.time():
            return self.cache[url]['content']
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
                html_content = page.content()
                browser.close()
                self.cache[url] = {'content': html_content, 'expiry': time.time() + self.cache_expiry}
                return html_content
        except Exception as e:
            print(f"Error fetching {url} with Playwright: {e}")
            return None

    def scrape_texts(self, url, min_result_length=50):
        html_content = self.fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, self.parser)
            texts = [element.string for element in soup.find_all(string=True) 
                     if element.parent.name not in ['style', 'script', 'head', 'title', 'meta', '[document]']]
            cleaned_texts = [re.sub(r'\s+', ' ', text.strip()) for text in texts if text and len(text.strip()) >= min_result_length]
            return " ".join(cleaned_texts)
        return []

    def scrape_links(self, url):
        html_content = self.fetch_html(url)
        if html_content:
            soup = BeautifulSoup(html_content, self.parser)
            return [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
        return []

if __name__ == "__main__":
    scraper = WebReader(headless=False, timeout=10)
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    min_result_length = 50
    clean_texts = scraper.scrape_texts(url, min_result_length)
    links = scraper.scrape_links(url)
    print(clean_texts)