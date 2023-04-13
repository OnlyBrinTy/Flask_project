from flask import *
from text_analysis import post_request
from parse import ParseApp
from data import db_session
from data.users import User
from form import LoginForm, RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required

app = Flask(__name__)
parse_app = ParseApp('https://republic.ru', 10)
app.config['SECRET_KEY'] = 'project_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/target')
def action_page_load():
    button_id = int(request.args.get('post'))
    articles = parse_app.get_articles_content(button_id)

    params = {'css_file_name': 'articles_page.css',
              'js_file_name': 'articles_page.js',
              'paragraphs': articles}

    return render_template('articles_page.html', **params)


@app.route('/')
def first_page_load():
    db_sess = db_session.create_session()
    params = {'css_file_name': 'main_page.css',
              'js_file_name': 'main_page.js',
              'articles_covers': parse_app.articles_covers}

    return render_template('main_page.html', **params)


@app.route('/DATA_text_from_speech', methods=['POST'])
def final_result_load():
    req = request.json
    audio_repeat = req['audio']
    text = req['text']

    response_result = post_request(audio_repeat, text)

    return response_result


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
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


@app.route('/success')
def success():
    return 'success'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            # about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        # return redirect('/login')
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_name = "db/members.db"
    db_session.global_init(db_name)
    app.run()
