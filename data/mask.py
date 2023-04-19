from sqlalchemy import *
from .db_session import SqlAlchemyBase


class Mask(SqlAlchemyBase):
    __tablename__ = 'masks'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    article_id = Column(Integer(), ForeignKey("articles.id"), nullable=False)
    # article_id = Column(Integer(), autoincrement=True, nullable=False)
    user_id = Column(Integer(), ForeignKey("users.id"), nullable=False)
    read_par = Column(String(), nullable=False)
