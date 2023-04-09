from flask import Flask, render_template, request
from text_analysis import post_request
from parse import ParseApp
from data import db_session
from data.users import User
from form import LoginForm, RegisterForm


app = Flask(__name__)
parse_app = ParseApp('https://republic.ru', 10)


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
        return redirect('/success')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    app.run()
