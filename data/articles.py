from sqlalchemy import Column, String, Integer, orm
from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase):
    """Этот класс отвечает за статьи, взятые с republic.ru.
     Помимо двух основных параметров - title и author, здесь параметр paragraphs.
     Он представляет собой список со ссылками на параграфы статьи """

    __tablename__ = 'articles'

    id = Column(Integer(), autoincrement=True, primary_key=True)
    title = Column(String(), nullable=False, index=True)
    author = Column(String(), nullable=False, index=True)

    paragraphs = orm.relationship("Paragraph")
    # masks = orm.relationship("Mask")
