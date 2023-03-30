from flask import Flask, render_template, request
from parse import ParseApp

app = Flask(__name__)
parse_app = ParseApp('https://republic.ru')


@app.route('/DATA_authors_and_titles', methods=['POST'])
def first_data_load():
    response = parse_app.get_articles()

    return response


@app.route('/DATA_request', methods=['POST'])
def text_data_load():
    button_id = int(request.args.get('param'))
    response = parse_app.get_articles_content(button_id)

    return response


@app.route('/ActionPage')
def action_page_load():
    return render_template('PhoneAppSecondPage.html')


@app.route('/')
def first_page_load():
    return render_template('index.html')


@app.route('/DATA_audio_text', methods=['POST'])
def final_result_load():
    req = request.json
    audio_repeat = req['audio']
    text = req['text']
    response_result = parse_app.get_correct_text(audio_repeat, text)

    return response_result


if __name__ == '__main__':
    app.run()
