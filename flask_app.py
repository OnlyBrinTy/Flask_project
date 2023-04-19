from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from datetime import date
from flask import *
from data import db_session
from text_analysis import *
from parse import *
from data.users import *
from form import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'memorizeme_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_name = "db/database.db"
db_session.global_init(db_name)
db_sess = db_session.create_session()

parse_app = ParseApp('https://republic.ru', 10, db_sess)


@app.route('/target')
def article_page_load():
    article_id = int(request.args.get('post'))
    article = parse_app.get_articles_content(article_id)

    params = {'css_file_name': 'articles_page.css',
              'js_file_name': 'articles_page.js',
              'paragraphs': article}

    return render_template('articles_page.html', **params)


@app.route('/')
def home_page_load():
    articles_covers = parse_app.load_articles_covers()
    params = {'css_file_name': 'main_page.css',
              'js_file_name': 'main_page.js',
              'is_registered': False,
              'articles_covers': articles_covers}

    return render_template('main_page.html', **params)


@app.route('/DATA_text_from_speech', methods=['POST'])
def final_result_load():
    if current_user:
        current_user.completed_tasks += 1

    req = request.json
    transcript = req['transcript']
    actual_text = req['text']

    response = post_request(transcript, actual_text)

    return response


@app.route('/DATA_delete_paragraph', methods=['POST'])
def delete_paragraph_from_article():
    req = request.json
    paragraph_id = req['id']

    parse_app.delete_paragraph(paragraph_id)

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


@app.route('/logout')
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
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def go_to_profile():
    forms = (EditPhoto(), EditPassword(), EditEmail(), LogOut())

    if any(map(FlaskForm.validate_on_submit, forms)):
        if forms[0].validate_on_submit():
            filename = secure_filename(forms[0].change_avatar.data.filename)
            forms[0].change_avatar.data.save('static/samples/' + filename)

            current_user.avatar_path = filename
        elif forms[1].validate_on_submit():
            current_user.set_password(forms[1].password.data)
        else:
            current_user.email = forms[2].email.data

        db_sess.merge(current_user)
        db_sess.commit()

    params = {
        'username': current_user.name,
        'user_avatar': current_user.avatar_path,
        'registration_date': current_user.registration_date,
        'completed_tasks': current_user.completed_tasks,
        'forms': forms,
        'title': 'Профиль'
    }

    return render_template('profile.html', **params)


if __name__ == '__main__':
    app.run()
