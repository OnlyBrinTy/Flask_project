import requests
import time
import string
import pymorphy2
from bs4 import BeautifulSoup

NUM_ARTICLES_TO_PARSE = 10


class ParseApp:
    update_interval = 86400

    def __init__(self, host):
        self.timer = 0
        self.host = host

    def get_articles(self):
        lapse = time.time() - self.timer

        if lapse >= self.update_interval or not self.timer:
            self.get_new_articles(50, NUM_ARTICLES_TO_PARSE)
            self.timer = time.time()

        return self.articles_covers

    def get_new_articles(self, attempts_num, titles_num):
        page = self.get_html(self.host)
        last_post = self.get_post(page)

        authors = []
        titles = []
        self.articles_content = {}

        while attempts_num and len(titles) < titles_num:
            post_url = f'{self.host}/posts/{last_post - i}'
            html = self.get_html(post_url)

            author = self.get_author(html.text)
            title = self.get_title(html.text)

            if author == title:
                print(author, title)
                continue
            elif not author and title:
                author = 'Нет автора'

            authors.append(author)
            titles.append(title)
            self.articles_content[post_url] = ''

        assert len(self.articles_urls) == NUM_ARTICLES_TO_PARSE

        self.articles_covers = {'authors': authors, 'titles': titles}

    def get_correct_text(self, aud_txt, rel_txt):
        aud_tok, real_tok = self.delete_extra_parts(aud_txt), self.delete_extra_parts(rel_txt)
        aud_bgram, real_bgram = self.get_bgramms(aud_tok), self.get_bgramms(real_tok)

        comparison = [g in real_bgram for g in aud_bgram]
        similarity = comparison.count(True) / len(comparison)

        return {'_': similarity}

    def get_articles_content(self, button_id):
        url_of_article = self.articles_content.keys()[button_id - 1]

        if not self.articles_content[url_of_article]:
            html_of_article = self.get_html(url_of_an_article)
            self.articles_content[url_of_article] = self.get_text(html_of_article.text)

        return {'_': self.articles_content[url_of_article]}

    def get_author(self, html_text):
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

    def get_post(self, page):
        soup = BeautifulSoup(page.text, 'html.parser')
        items = soup.find('a', class_='card__link').get('href')
        last_post = int(items.replace('/posts/', ''))

        return last_post

    def get_html(self, url, parameters=''):
        return requests.get(url, params=parameters)

    def get_bgramms(self, tokens):
        return tuple((tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1))

    def delete_extra_parts(self, text):
        morph = pymorphy2.MorphAnalyzer()
        tokens = text.translate(str.maketrans('', '', string.punctuation)).lower().split()
        clear_tokens = tuple(
            filter(lambda x: morph.parse(x)[0].tag.POS not in ('CONJ', 'PRCL', 'INTJ', 'PREP'), tokens))

        return clear_tokens
