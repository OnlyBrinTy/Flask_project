from bs4 import BeautifulSoup
import requests
import re

URL = 'https://api.diffchecker.com/public/text?output_type=html&email=belowzero2009@yandex.ru'
HEADERS = {
    'Content-type': 'application/json'
}


def format_html(html):
    """Удаление лишних элементов после получения статьи"""
    soup = BeautifulSoup(html, 'html.parser')

    diff_line_num1, diff_line_num2 = soup.find_all('td', class_='diff-line-number')
    diff_line_num1.replaceWith('')
    diff_line_num2.attrs['data-content'] = ''

    soup.find('style').replaceWith('')

    return str(soup).replace('line-height: 1rem;\n  ', '')


def post_request(text1, text2):
    """Обращаемся к API DiffChecker для получения сравнения двух текстов в виде html"""

    # приводим два текста в один формат
    removed_signs1 = re.sub(r'[^\w\s]', '', text1).lower()
    removed_signs2 = re.sub(r'[^\w\s]', '', text2).lower()

    data = {"left": removed_signs1,
            "right": removed_signs2,
            "diff_level": "word"}

    response = requests.post(URL, json=data, headers=HEADERS)

    formatted_html = format_html(response.text)

    return formatted_html
