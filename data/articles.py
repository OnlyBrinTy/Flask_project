from sqlalchemy import Column, String, Integer, orm
from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase):
    __tablename__ = 'articles'

    id = Column(Integer(), autoincrement=True, primary_key=True)
    title = Column(String(), nullable=False, index=True)
    author = Column(String(), nullable=False, index=True)

    paragraphs = orm.relationship("Paragraph")
