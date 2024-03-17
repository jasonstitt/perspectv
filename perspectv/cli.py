import click
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import search, model


@click.command()
@click.argument("domain")
@click.option("--dbfile", default="perspectv.db", help="Filename for sqlite database")
def main(domain, dbfile):
    print(f"Summarizing {domain}...")
    engine = create_engine(f"sqlite:///{dbfile}")
    model.Base.metadata.create_all(engine)
    num_found_urls = 0
    with Session(engine) as session:
        for url in search.fetch_urls(domain):
            url_obj = model.Url(original_url=url)
            try:
                session.add(url_obj)
                session.commit()
                num_found_urls += 1
            except IntegrityError:
                session.rollback()
    print(f"Found {num_found_urls} new urls")
