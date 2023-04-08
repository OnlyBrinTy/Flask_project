from flask import Flask, render_template, request
from text_analysis import post_request
from parse import ParseApp

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


if __name__ == '__main__':
    app.run()
