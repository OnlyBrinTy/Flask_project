# -*- coding: utf-8 -*-
import requests
import time
from bs4 import BeautifulSoup
import string
import pymorphy2


HEADERS = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.415'
    }

J = 10
K = 0
I = 50
HOST = 'https://republic.ru/'


class ParseApp:
    def __init__(self):
        self.timer = 0
        self.cache = {}
        self.X_AT = self.authors_and_titles(K, J, I, HOST)
        self.Text = []

    def get_corrected_text(self, aud_txt, rel_txt):
        aud_tok = self.delete_extra_parts(aud_txt)
        real_tok = self.delete_extra_parts(rel_txt)

        aud_bgram = self.get_bgramms(aud_tok)
        real_bgram = self.get_bgramms(real_tok)

        comparison = [g in real_bgram for g in aud_bgram]
        similarity = comparison.count(True) / len(comparison)

        return {'_': similarity}

    def delete_extra_parts(self, text):
        morph = pymorphy2.MorphAnalyzer()
        tokens = text.translate(str.maketrans('', '', string.punctuation)).lower().split()
        clear_tokens = tuple(
            filter(lambda w: morph.parse(w)[0].tag.POS not in ('CONJ', 'PRCL', 'INTJ', 'PREP'), tokens))

        return clear_tokens

    def get_bgramms(self, tokens):
        return tuple((tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1))

    def get_data(self):
        lapse = int(time.time() - self.timer)
        if lapse < 86400:
            return self.cache
        else:
            self.cache = {'DATA_author': [self.X_AT[0][0], self.X_AT[0][1], self.X_AT[0][2], self.X_AT[0][3], self.X_AT[0][4], self.X_AT[0][5], self.X_AT[0][6], self.X_AT[0][7], self.X_AT[0][8], self.X_AT[0][9]], 'DATA_title': [self.X_AT[1][0], self.X_AT[1][1], self.X_AT[1][2], self.X_AT[1][3], self.X_AT[1][4], self.X_AT[1][5], self.X_AT[1][6], self.X_AT[1][7], self.X_AT[1][8], self.X_AT[1][9]]}
            self.timer = time.time()
            return self.cache

    def authors_and_titles(self, K, J, I, HOST):
        page = self.get_html(HOST)
        X = self.get_post(page)
        DATA_author = []
        DATA_title = []
        URLs = []
        for _ in range(I):
            if K == J:
                break

            def get_author(html):
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.find_all('div', class_='post-authors__name')
                author = ''
                for item in items:
                    author = item.text.strip()

                return author


            def get_title(html):
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.find_all('h1', class_='post-title')
                titles = ''
                for item in items:
                    text = item.text
                    text = text.replace('\xa0', ' ').strip()
                    titles = text
                return titles



            URL = f'https://republic.ru/posts/{X - I}'
            html = self.get_html(URL)
            DATA_author.append(get_author(html.text))
            DATA_title.append(get_title(html.text))

            if len(DATA_author) and  len(DATA_title) > 0:
                if DATA_author[len(DATA_author) - 1] == DATA_title[len(DATA_title) - 1]:
                    del DATA_author[len(DATA_author) - 1]
                    del DATA_title[len(DATA_title) - 1]
                    I = I - 1
                    continue
                elif DATA_author[len(DATA_author) - 1] == '' and DATA_title[len(DATA_title) - 1] != '':
                    DATA_author[len(DATA_author) - 1] = 'Нет автора'

            I = I - 1
            K = K + 1
            URLs.append(URL)

        return DATA_author, DATA_title, URLs

    def text(self, URLs, BT_NUM):
        html = self.get_html(URLs[BT_NUM - 1])

        def get_text(html):
            return ''.join(p.get_text() for p in BeautifulSoup(html, 'html.parser').
                           find('div', class_='free-content').contents if len(p.text) > 100)

        DATA_text = get_text(html.text)
        self.Text = DATA_text
        DATA_text = {'_': DATA_text}
        return DATA_text

    def get_html(self, url, params=''):
        r = requests.get(url, headers=HEADERS, params=params)
        return r

    def get_post(self, page):
        soup = BeautifulSoup(page.text, 'html.parser')
        items = soup.find('a', class_='card__link').get('href')
        last_post = int(items.replace('/posts/', ''))
        return last_post

# a = ParseApp()
# print(a.get_corrected_text('трудно переоценить значение детских смесей в Соединенных Штатах. около 75% родителей первые 6 месяцев их жизни полагаются исключительно на готовые формулы. Из-за этого нынешний кризис на рынке смесей, возникший неожиданно для властей, волнует многие десятки миллионов американцев.', 'Значение детских смесей в Соединенных Штатах трудно переоценить. Известно, что около 75% родителей и нянек младенцев первые 6 месяцев их жизни полагаются исключительно на готовые формулы. Поэтому нынешний кризис на рынке смесей, возникший неожиданно для властей, волнует многие десятки миллионов американцев.'))