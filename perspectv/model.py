from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class Url(Base):
    """A URL we have discovered and its final URL after redirects"""

    __tablename__ = "url"
    original_url = mapped_column(String, primary_key=True)
    final_url = mapped_column(String)
    error = mapped_column(String)


class Page(Base):
    """The contents of a page we have scraped"""

    __tablename__ = "page"
    url = mapped_column(String, primary_key=True)
    body = mapped_column(String)
    extract = mapped_column(String)
