from sqlalchemy import *
from .db_session import SqlAlchemyBase


class Mask(SqlAlchemyBase):
    """Данный класс представляет их себя таблицу с маской параграфов для каждого зарегистрированного
     пользователя. Таким образом пользователю выводятся только непрочитанные параграфы."""

    __tablename__ = 'masks'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer(), ForeignKey("users.id"), nullable=False)

    read_par = Column(String(), nullable=False)
