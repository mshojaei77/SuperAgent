import asyncio
import random
from playwright.async_api import async_playwright

class PlaywrightWebReader:
    def __init__(self):
        pass

    async def human_like_delay(self, min_delay=1, max_delay=3):
        """Introduce a human-like delay between actions."""
        await asyncio.sleep(random.uniform(min_delay, max_delay))

    async def accept_cookies(self, page):
        """Attempt to accept cookies if a consent banner is present."""
        try:
            consent_button = await page.query_selector("button#accept-cookies, button[data-consent='accept']")
            if consent_button:
                await consent_button.click()
                await self.human_like_delay()
                print("Accepted cookies.")
        except Exception as e:
            print(f"Error accepting cookies: {e}")

    async def _scrape(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                accept_downloads=True,
                bypass_csp=True,
                color_scheme='light',
                device_scale_factor=1,
                has_touch=False,
                ignore_https_errors=True,
                is_mobile=True,
                java_script_enabled=True,
                locale='en-US',
                no_viewport=False,
                offline=False,
                reduced_motion='no-preference',
                service_workers='allow',
                strict_selectors=False,
                timezone_id='America/Los_Angeles',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
                viewport={'width': 1280, 'height': 720},
            )

            page = await context.new_page()
            await self.human_like_delay()

            try:
                await page.goto(url, timeout=60000)
            except Exception as e:
                print(f"Error navigating to {url}: {e}")
                await context.close()
                await browser.close()
                return None

            await self.human_like_delay()

            # Attempt to accept cookies
            await self.accept_cookies(page)

            # Simulate human-like scrolling
            await page.mouse.wheel(0, random.randint(300, 600))
            await self.human_like_delay()

            # Extract title
            title = await page.title()
            await self.human_like_delay()

            # Extract content from paragraphs within the main content area
            content_element = await page.query_selector("div#mw-content-text > div.mw-parser-output")
            if content_element:
                paragraphs = await content_element.query_selector_all("p")
                content = "\n".join([await p.text_content() for p in paragraphs])
            else:
                print("Content element not found.")
                content = ""

            await self.human_like_delay()

            await context.close()
            await browser.close()
            return {"title": title, "content": content}

    def scrape(self, url):
        return asyncio.run(self._scrape(url))


# Example usage
if __name__ == "__main__":
    scraper = PlaywrightWebReader()
    url = "https://twitter.com/SpaceX/status/1795463423066792387"
    texts = scraper.scrape(url)
    print(texts)