from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class Url(Base):
    __tablename__ = "url"
    original_url = mapped_column(String, primary_key=True)
    final_url = mapped_column(String)
