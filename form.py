from flask_wtf import *
from wtforms import *
from wtforms.validators import *


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class Profile(FlaskForm):
    email = EmailField('Сменить почту', validators=[DataRequired()])
    submit_email = SubmitField('Изменить')

    password = PasswordField('Сменить пароль', validators=[DataRequired()])
    submit_password = SubmitField('Изменить')

    logout = SubmitField('Выйти')
