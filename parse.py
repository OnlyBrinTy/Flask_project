import requests
import time
import string
import pymorphy2
from bs4 import *

HEADINGS = {
    'accept': '''text/html,application/xhtml+xml,application/xml;q=0.9,image/
                avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9''',
    'user-agent': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/
                87.0.4280.141 Safari/537.36 OPR/73.0.3856.415'''
}

K = 0
J = 10
I = 50
SERVER_HOST = 'https://republic.ru/'


class ParseApp:
    def __init__(self):
        self.timer = 0
        self.cache = {}
        self.X_AT = self.authors_and_titles(K, J, I, SERVER_HOST)
        self.text = []

    def get_correct_text(self, aud_txt, rel_txt):
        aud_tok, real_tok = self.delete_extra_parts(aud_txt), self.delete_extra_parts(rel_txt)
        aud_bgram, real_bgram = self.get_bgramms(aud_tok), self.get_bgramms(real_tok)

        comparison = [g in real_bgram for g in aud_bgram]
        similarity = comparison.count(True) / len(comparison)

        return {'_': similarity}

    def get_data(self):
        lapse = int(time.time() - self.timer)

        if lapse < 24 * 60 * 60:
            return self.cache
        else:
            self.cache = {'data_author': [self.X_AT[0][0], self.X_AT[0][1], self.X_AT[0][2], self.X_AT[0][3],
                                          self.X_AT[0][4], self.X_AT[0][5], self.X_AT[0][6], self.X_AT[0][7],
                                          self.X_AT[0][8], self.X_AT[0][9]],
                          'data_title': [self.X_AT[1][0], self.X_AT[1][1], self.X_AT[1][2], self.X_AT[1][3],
                                         self.X_AT[1][4], self.X_AT[1][5], self.X_AT[1][6], self.X_AT[1][7],
                                         self.X_AT[1][8], self.X_AT[1][9]]}
            self.timer = time.time()

            return self.cache

    def authors_and_titles(self, k, j, i, server_host):
        page = self.get_html(server_host)
        page_post = self.get_post(page)

        data_author = []
        data_title = []
        URLs = []

        for _ in range(i):
            if k == j:
                break

            URL = f'https://republic.ru/posts/{page_post - i}'
            html = self.get_html(URL)
            data_author.append(self.get_author(html.text))
            data_title.append(self.get_title(html.text))

            if len(data_author) and len(data_title) > 0:
                if data_author[len(data_author) - 1] == data_title[len(data_title) - 1]:
                    del data_author[len(data_author) - 1]
                    del data_title[len(data_title) - 1]
                    i -= 1
                    continue
                elif data_author[len(data_author) - 1] == '' and data_title[len(data_title) - 1] != '':
                    data_author[len(data_author) - 1] = 'Нет автора'

            i -= 1
            k += 1
            URLs.append(URL)

        return data_author, data_title, URLs

    def text(self, URLs, BT_NUM):
        html = self.get_html(URLs[BT_NUM - 1])

        data_text = self.get_text(html.text)
        self.text = data_text
        data_text = {'_': data_text}

        return data_text

    @staticmethod
    def get_author(html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        items = soup.find_all('div', class_='post-authors__name')
        author = ''

        for item in items:
            author = item.text.strip()

        return author

    @staticmethod
    def get_title(html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        items = soup.find_all('h1', class_='post-title')
        titles = ''

        for item in items:
            text = item.text
            text = text.replace('\xa0', ' ').strip()
            titles = text

        return titles

    @staticmethod
    def get_text(html):
        return ''.join(p.get_text() for p in BeautifulSoup(html, 'html.parser').
                       find('div', class_='free-content').contents if len(p.text) > 100)

    @staticmethod
    def get_post(page):
        soup = BeautifulSoup(page, 'html_parser')
        items = soup.find('a', class_='card__link').get('href')
        last_post = int(items.replace('/posts/', ''))

        return last_post

    @staticmethod
    def get_html(url, parameters=''):
        return requests.get(url, headers=HEADINGS, params=parameters)

    @staticmethod
    def get_bgramms(tokens):
        return tuple((tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1))

    @staticmethod
    def delete_extra_parts(text):
        morph = pymorphy2.MorphAnalyzer()
        tokens = text.translate(str.maketrans('', '', string.punctuation)).lower().split()
        clear_tokens = tuple(
            filter(lambda x: morph.parse(x)[0].tag.POS not in ('CONJ', 'PRCL', 'INTJ', 'PREP'), tokens))

        return clear_tokens
