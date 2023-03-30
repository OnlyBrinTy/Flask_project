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

        self.get_articles()

    def get_articles(self):
        lapse = time.time() - self.timer

        if lapse >= self.update_interval:
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
            attempts_num -= 1

            post_url = f'{self.host}/posts/{last_post - attempts_num}'
            html = self.get_html(post_url)
            author = self.get_author(html.text)
            title = self.get_title(html.text)

            if not author:
                if not title:
                    continue

                author = 'Нет автора'

            authors.append(author)
            titles.append(title)
            self.articles_content[post_url] = ''

        self.articles_covers = {'authors': authors, 'titles': titles}

    def get_correct_text(self, aud_txt, rel_txt):
        aud_tok, real_tok = self.delete_extra_parts(aud_txt), self.delete_extra_parts(rel_txt)
        aud_bgram, real_bgram = self.get_bgramms(aud_tok), self.get_bgramms(real_tok)

        comparison = [g in real_bgram for g in aud_bgram]
        similarity = comparison.count(True) / len(comparison)

        return {'_': similarity}

    def get_articles_content(self, button_id):
        url_of_article = list(self.articles_content)[button_id - 1]

        if not self.articles_content[url_of_article]:
            html_of_article = self.get_html(url_of_article)
            self.articles_content[url_of_article] = self.get_text(html_of_article.text)

        return {'_': self.articles_content[url_of_article]}

    def get_author(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        item = soup.find('div', class_='post-authors__name')
        author = item.text.strip() if item else None

        return author

    @staticmethod
    def get_title(html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        item = soup.find('h1', class_='post-title')
        title = item.text.replace('\xa0', ' ').strip() if item else None

        return title

    @staticmethod
    def get_text(html):
        soup = BeautifulSoup(html, 'html.parser').find('div', class_='free-content').contents

        paragraphs = []
        for p in soup:
            if len(p.text) > 100:
                paragraphs.append(p.get_text())

        return paragraphs

    def get_post(self, page):
        soup = BeautifulSoup(page.text, 'html.parser')
        items = soup.find('a', class_='card__link').get('href')
        last_post = int(items.replace('/posts/', ''))

        return last_post

    def get_html(self, url):
        return requests.get(url)

    def get_bgramms(self, tokens):
        return tuple((tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1))

    def delete_extra_parts(self, text):
        morph = pymorphy2.MorphAnalyzer()
        tokens = text.translate(str.maketrans('', '', string.punctuation)).lower().split()
        clear_tokens = tuple(
            filter(lambda x: morph.parse(x)[0].tag.POS not in ('CONJ', 'PRCL', 'INTJ', 'PREP'), tokens))

        return clear_tokens
