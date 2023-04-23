from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from itertools import compress
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from data import db_session
from text_analysis import post_request
from parse import ParseApp
from data.users import User
from data.mask import Mask
from form import RegisterForm, LoginForm, EditPhoto, EditPassword, EditEmail, LogOut

app = Flask('foo')
app.config['SECRET_KEY'] = 'memorizeme_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


# создаём сессию sqlalchemy
db_name = "db/database.db"
db_session.global_init(db_name)
db_sess = db_session.create_session()

# инициализируем парсер для сайта republic.ru, с которого берём 10 статей.
# Также даём ему сессию БД
parse_app = ParseApp('https://republic.ru', 10, False, db_sess)


@app.route('/<int:article_id>')
def article_page_load(article_id):
    """Страница с содержимым статьи"""

    # загружаем содержание статьи (параграфы)
    article = parse_app.get_articles_content(article_id)

    if current_user.is_authenticated:
        # если пользователь уже закрыл какой-то абзац,
        # то он помечается в маске для этой статьи как 0 и не отображается на странице
        mask = map(int, current_user.masks[article_id - 1].read_par)

        article = list(compress(article, mask))

    params = {'css_file_name': 'articles_page.css',
              'js_file_name': 'articles_page.js',
              'is_registered': current_user.is_authenticated,
              'paragraphs': article}

    return render_template('articles_page.html', **params)


@app.route('/')
def home_page_load():
    """Начальная страница с заголовками статей"""

    # загружаем обложки статей (авторы и названия статей)
    articles_covers = parse_app.load_articles_covers()
    params = {'css_file_name': 'main_page.css',
              'js_file_name': 'main_page.js',
              'is_registered': current_user.is_authenticated,
              'articles_covers': articles_covers}

    return render_template('main_page.html', **params)


@app.route('/DATA_text_from_speech', methods=['POST'])
def final_result_load():
    """Обработка запроса на вывод результата сравнения абзаца с пересказанным текстом"""

    if current_user.is_authenticated:
        # Добавляем 1 к счётчику выполненных заданий если авторизован
        current_user.completed_tasks += 1

    req = request.json
    transcript = req['transcript']
    actual_text = req['text']

    # получаем html сравнения от API
    response = post_request(transcript, actual_text)

    return response


@app.route('/DATA_delete_paragraph', methods=['POST'])
@login_required
def delete_paragraph_from_article():
    """Удалить параграф из маски если его закрыл авторизованный пользователь"""

    req = request.json
    paragraph_id = req['paragraph_id']
    article_id = int(req['article_id'])
    deleted_blocks = req['deleted_blocks']

    # обращаемся к маске, относящаяся к его статье
    mask = current_user.masks[article_id - 1]

    # преобразуем строку из 0 и 1 в список
    list_mask = list(mask.read_par)
    ones_indexes = [i for i, n in enumerate(list_mask) if n == '1']

    shift = len(sorted(deleted_blocks)[:deleted_blocks.index(paragraph_id)])
    index = paragraph_id - 1 - shift
    list_mask[ones_indexes[index]] = '0'  # отмечаем параграф как выполненный
    mask.read_par = ''.join(list_mask)

    db_sess.merge(mask)
    db_sess.commit()

    return {}


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()

    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        # Добавляем маску параграфов для пользователя
        for mask_length in parse_app.masks_lengths:
            db_sess.add(Mask(user_id=user.id, read_par='1' * mask_length))

        db_sess.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def go_to_profile():
    """Профиль пользователя"""

    # загружаем формы для взаимодействия с аккаунтом
    forms = (EditPhoto(), EditPassword(), EditEmail(), LogOut())
    params = {
        'username': current_user.name,
        'user_avatar': current_user.avatar_path,
        'registration_date': current_user.registration_date,
        'completed_tasks': current_user.completed_tasks,
        'forms': forms,
        'title': 'Профиль'
    }

    if any(map(FlaskForm.validate_on_submit, forms)):   # хоть одна кнопка нажата
        if forms[0].validate_on_submit():
            # смена фото профиля
            filename = secure_filename(forms[0].change_avatar.data.filename)
            # загружаем картинку в папку
            forms[0].change_avatar.data.save('static/samples/' + filename)
            current_user.avatar_path = filename
        elif forms[1].validate_on_submit():
            # смена пароля
            if forms[1].new_password.data != forms[1].new_password_again.data:
                return render_template('profile.html', **params, message2="Пароли не совпадают")

            current_user.set_password(forms[1].new_password.data)
        else:
            # смена почты
            user_with_this_email = db_sess.query(User).filter(User.email == forms[2].email.data).first()
            if user_with_this_email:
                return render_template('profile.html', **params, message1="Такая почта уже есть")

            current_user.email = forms[2].email.data

        # загружаем параметры ещё раз на случай если что-то поменяется
        params = {
            'username': current_user.name,
            'user_avatar': current_user.avatar_path,
            'registration_date': current_user.registration_date,
            'completed_tasks': current_user.completed_tasks,
            'forms': forms,
            'title': 'Профиль'
        }

        db_sess.merge(current_user)
        db_sess.commit()

    return render_template('profile.html', **params)


if __name__ == '__main__':
    app.run()
