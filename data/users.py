import datetime
import sqlalchemy
from flask_login import *
from sqlalchemy import *
from werkzeug.security import *

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    masks = orm.relationship("Mask")

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    avatar_path = sqlalchemy.Column(sqlalchemy.String, default='no image.png')
    registration_date = sqlalchemy.Column(sqlalchemy.Date, default=datetime.date.today)
    completed_tasks = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
