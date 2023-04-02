from flask import *
from parse import *
from flask_login import *
from data.users import *
from data import db_session
from form import *

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

parse_app = ParseApp()
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/DATA_authors_and_titles', methods=['POST'])
def first_data_load():
    response = parse_app.get_data()
    return response


@app.route('/DATA_request', methods=['POST'])
def text_data_load():
    BT_NUM = int(request.args.get('param'))
    response = parse_app.text(parse_app.X_AT[2], BT_NUM)
    return response


@app.route('/ActionPage', methods=['GET'])
def ActionPage_load():
    return render_template('PhoneAppSecondPage.html')


@app.route('/', methods=['GET'])
def first_page_load():
    return render_template('PhoneApp.html')


@app.route('/DATA_audio_text', methods=['POST'])
def final_result_load():
    req = request.json
    audio_repeat = req['audio']
    text = req['text']
    response_result = parse_app.get_correct_text(audio_repeat, text)
    return response_result


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
    app.run(debug=False, host='0.0.0.0', port=443, ssl_context='adhoc')
