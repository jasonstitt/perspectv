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
@click.option(
    "--model-report",
    default="google/gemini-pro",
    help="Model for report generation (high strength, high cost)",
)
def main(domain, dbfile, model_summary, model_report):
    print(f"Summarizing {domain}...")
    engine = create_engine(f"sqlite:///{dbfile}")
    model.Base.metadata.create_all(engine)
    run_discover(engine, domain)
    run_scrape(engine)
    run_extract(engine, model_summary)
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
        # Dedupe the URLs
        by_original = {url.original_url: url for url in urls}
        results = scrape.scrape(by_original.keys())
        print(f"Scraped {len(results)} pages")
        # Save the final urls so we have the redirect map
        for result in results:
            url = by_original[result.original_url]
            url.final_url = result.final_url
            url.error = result.error
            if not result.error:
                page = model.Page(url=result.final_url, body=result.body)
                session.add(page)
            session.commit()


def run_extract(engine, model_summary):
    with Session(engine) as session:
        pages = session.query(model.Page).filter(model.Page.extract.is_(None)).all()
        for page in pages:
            summary = llm.run_prompt("page_extract", model_summary, text=page.body)
            page.extract = summary
            session.commit()


def run_reports(engine, model_report):
    with Session(engine) as session:
        pages = session.query(model.Page).all()
        text = "\n------\n".join(page.extract for page in pages)
    report_names = ["summary"]
    reports = [
        llm.run_prompt(f"report_{name}", model_report, text=text)
        for name in report_names
    ]
    for report in reports:
        print(report)
