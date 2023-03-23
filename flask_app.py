from flask import *
from parse import *

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

parse_app = ParseApp()


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


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=443, ssl_context='adhoc')
