import click
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from . import search, model, scrape, llm


@click.command()
@click.argument("domain")
@click.option("--dbfile", default="perspectv.db", help="Filename for sqlite database")
@click.option(
    "--model-extract",
    default="google/gemini-pro",
    help="Model for extracting text (low cost, med strength)",
)
@click.option(
    "--model-report",
    default="google/gemini-pro", #"anthropic/claude-3-opus",
    help="Model for report generation (large context)",
)
def main(domain, dbfile, model_extract, model_report):
    engine = create_engine(f"sqlite:///{dbfile}")
    model.Base.metadata.create_all(engine)
    run_discover(engine, domain)
    run_scrape(engine)
    run_extract(engine, model_extract)
    run_reports(engine, model_report)


def run_discover(engine, domain):
    with Session(engine) as session:
        # Fetch URLs we already found
        urls = session.query(model.Url).all()
        # Discover URLs using search
        if not urls:
            print(f"Discovering URLs for {domain}...")
            for url in search.fetch_urls(domain):
                url_obj = model.Url(original_url=url)
                session.add(url_obj)
            session.commit()


def run_scrape(engine):
    with Session(engine) as session:
        # Scrape all the pages that haven't been scraped yet
        urls = (
            session.query(model.Url)
            .filter(model.Url.final_url.is_(None), model.Url.error.is_(None))
            .all()
        )
        # Scrape the discovered URLs
        by_original = {url.original_url: url for url in urls}
        results = scrape.scrape(by_original.keys())
        print(f"Scraped {len(results)} pages")
        # Save the final urls so we have the redirect map
        existing_pages = session.query(model.Page).all()
        seen_final_urls = set(x.url for x in existing_pages)
        for result in results:
            url = by_original[result.original_url]
            url.final_url = result.final_url
            url.error = result.error
            if not result.error and result.final_url not in seen_final_urls:
                page = model.Page(url=result.final_url, body=result.body)
                session.add(page)
                seen_final_urls.add(result.final_url)
                session.commit()


def run_extract(engine, model_extract):
    with Session(engine) as session:
        pages = session.query(model.Page).filter(model.Page.extract.is_(None)).all()
        for page in pages:
            summary = llm.run_prompt("page_extract", model_extract, text=page.body)
            print(f"Extracted {page.url}")
            page.extract = summary
            session.commit()


def run_reports(engine, model_report):
    with Session(engine) as session:
        reports = session.query(model.Report).all()
        existing_reports = set(x.name for x in reports)
        pages = session.query(model.Page).all()
        text = "\n------\n".join(page.extract for page in pages)
        for name in ["summary", "products", "swot", "software"]:
            if name in existing_reports:
                continue
            body = llm.run_prompt(f"report_{name}", model_report, text=text)
            session.add(model.Report(name=name, body=body))
            session.commit()
            print(f"Generated report {name}")
