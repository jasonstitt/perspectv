import click
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import search, model, scrape


@click.command()
@click.argument("domain")
@click.option("--dbfile", default="perspectv.db", help="Filename for sqlite database")
def main(domain, dbfile):
    print(f"Summarizing {domain}...")
    engine = create_engine(f"sqlite:///{dbfile}")
    model.Base.metadata.create_all(engine)
    with Session(engine) as session:
        urls = session.query(model.Url).all()
        if not urls:
            for url in search.fetch_urls(domain):
                url_obj = model.Url(original_url=url)
                session.add(url_obj)
                urls.append(url_obj)
            session.commit()
        print(f"Found {len(urls)} URLs")
        by_original = {url.original_url: url for url in urls}
        to_scrape = [url.original_url for url in urls if not url.final_url]
        print(f"Scraping {len(to_scrape)} URLs")
        results = scrape.scrape(to_scrape)
        for result in results:
            url = by_original[result.original_url]
            url.final_url = result.final_url
            url.body = result.body
            session.commit()
