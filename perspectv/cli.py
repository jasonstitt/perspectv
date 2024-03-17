import click
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import search, model, scrape, llm


@click.command()
@click.argument("domain")
@click.option("--dbfile", default="perspectv.db", help="Filename for sqlite database")
@click.option(
    "--model-summary",
    default="google/gemini-pro",
    help="Model for summarization (low cost, med strength)",
)
def main(domain, dbfile, model_summary):
    print(f"Summarizing {domain}...")
    engine = create_engine(f"sqlite:///{dbfile}")
    model.Base.metadata.create_all(engine)
    with Session(engine) as session:
        # Fetch URLs we already found
        urls = session.query(model.Url).all()
        # Discover URLs using search
        if not urls:
            for url in search.fetch_urls(domain):
                url_obj = model.Url(original_url=url)
                session.add(url_obj)
                urls.append(url_obj)
            session.commit()
        print(f"Found {len(urls)} URLs")
        # Scrape all the pages that haven't been scraped yet
        by_original = {url.original_url: url for url in urls}
        to_scrape = [url.original_url for url in urls if not url.final_url]
        print(f"Scraping {len(to_scrape)} URLs")
        results = scrape.scrape(to_scrape)
        # Save the final urls so we have the redirect map
        for result in results:
            url = by_original[result.original_url]
            url.final_url = result.final_url
            session.commit()
        # Extract the page contents
        by_final = {result.final_url: result for result in results if result.final_url}
        for final_url, result in by_final.items():
            summary = llm.run_prompt("page_extract", model_summary, text=result.body)
            print(final_url, summary)
