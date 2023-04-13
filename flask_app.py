from flask import Flask, render_template, request, redirect
from text_analysis import post_request
from parse import ParseApp
# from data import db_session
# from data.users import User
# from form import LoginForm, RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'memorizeme_secret_key'
parse_app = ParseApp('https://republic.ru', 10)


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
              'articles_covers': articles_covers}

    return render_template('main_page.html', **params)


@app.route('/DATA_text_from_speech', methods=['POST'])
def final_result_load():
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
