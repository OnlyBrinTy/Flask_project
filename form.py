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


class EditPhoto(FlaskForm):
    change_avatar = FileField('Выбрать', validators=[DataRequired()])

    submit_avatar = SubmitField('Изменить')


class EditPassword(FlaskForm):
    new_password = PasswordField('Введите новый пароль', validators=[DataRequired()])
    new_password_again = PasswordField('Введите новый пароль ещё раз', validators=[DataRequired()])

    submit_password = SubmitField('Изменить')


class EditEmail(FlaskForm):
    email = EmailField('Изменить почту', validators=[DataRequired()])

    submit_email = SubmitField('Изменить')


class LogOut(FlaskForm):
    logout = SubmitField('Выйти')
