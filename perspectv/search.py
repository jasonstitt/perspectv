from duckduckgo_search import DDGS


def fetch_urls(domain, max_results=1000):
    for row in DDGS().text(f"site:{domain}", max_results=max_results):
        yield row["href"]
