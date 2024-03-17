import asyncio
from aiostream import stream
from playwright.async_api import async_playwright
from collections import namedtuple

ScrapeResult = namedtuple(
    "ScrapeResult", ["original_url", "final_url", "body", "error"]
)


async def scrape_page(browser, url):
    try:
        page = await browser.new_page()
        await page.goto(url)
        body_text = await page.inner_text("body")
        final_url = page.url
        print(f"Scraped {url}")
        await page.close()
        return ScrapeResult(
            original_url=url, final_url=final_url, body=body_text, error=None
        )
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        await page.close()
        return ScrapeResult(original_url=url, final_url=None, body=None, error=str(e))


async def run_scrapes(urls):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        inputs = stream.iterate((browser, x) for x in urls)
        results = stream.starmap(inputs, scrape_page, ordered=False, task_limit=5)
        results = await stream.list(results)
        await browser.close()
        return results


def scrape(urls):
    urls = [x for x in urls if not x.endswith(".pdf")]
    return asyncio.run(run_scrapes(urls))
