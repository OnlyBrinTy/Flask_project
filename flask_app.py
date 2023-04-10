from flask import Flask, render_template, request
from text_analysis import post_request
from parse import ParseApp

app = Flask(__name__)
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
    params = {'css_file_name': 'main_page.css',
              'js_file_name': 'main_page.js',
              'articles_covers': parse_app.articles_covers}

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

    response = parse_app.delete_paragraph(paragraph_id)

    return {'article_is_empty': response}


if __name__ == '__main__':
    app.run()
