from sqlalchemy import *
from .db_session import SqlAlchemyBase


class Paragraph(SqlAlchemyBase):
    """Данный класс представляет их себя таблицу с параграфами, которые ссылаются на статьи
    по article_id. Таким образом article получает доступ к списку параграфов статьи."""

    __tablename__ = 'paragraphs'

    id = Column(Integer(), autoincrement=True, primary_key=True)
    article_id = Column(Integer(), ForeignKey("articles.id"), nullable=False)
    num = Column(Integer(), nullable=False)

    text = Column(String(), nullable=False, index=True)

    def __str__(self):
        return self.text
