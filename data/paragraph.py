from sqlalchemy import Column, String, Integer, ForeignKey, Identity
from .db_session import SqlAlchemyBase


class Paragraph(SqlAlchemyBase):
    __tablename__ = 'paragraphs'

    id = Column(Integer(), autoincrement=True, primary_key=True)
    article_id = Column(Integer(), ForeignKey("articles.id"), nullable=False)
    num = Column(Integer(), nullable=False)
    text = Column(String(), nullable=False, index=True)
    is_read = Column(Integer(), nullable=True, default=0)

    def __str__(self):
        return self.text
