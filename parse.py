from itertools import islice
from bs4 import BeautifulSoup, Tag
import requests
import time


def batched(iterable, n):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield ' '.join(piece)
        piece = list(islice(i, n))


class ParseApp:
    update_interval = 86400

    def __init__(self, host: str, num_articles_to_parse: int):
        self.num_articles_to_parse = num_articles_to_parse
        self.host = host

        self.timer = 0
        self.chunk_size = 30
        self.titles_num = 10
        self.articles_covers = []
        self.articles_content = {}

        self.update_articles()

    def update_articles(self):
        lapse = time.time() - self.timer

        if lapse >= self.update_interval:
            main_page_html = self.get_html(self.host)
            main_page_soup = BeautifulSoup(main_page_html.text, 'html.parser')
            self.curr_post_id = self.get_last_article(main_page_soup)

            self.get_content()
            self.timer = time.time()

    def get_content(self):
        def get_author(soup):
            item = soup.find('div', class_='post-authors__name')
            author_name = item.text.strip() if item else None

            return author_name

        def get_title(soup):
            item = soup.find('h1', class_='post-title')
            title_name = item.text.replace('\xa0', ' ').strip() if item else None

            return title_name

        def get_content(soup, chunk_size):
            extra_classes = ('caption', 'credit')

            item = soup.find('div', class_='free-content')
            paragraphs = item.find_all('p', class_=lambda c: c not in extra_classes)

            words = ' '.join(map(Tag.get_text, paragraphs)).split()
            chunks = list(batched(words, chunk_size))
            if len(chunks[-1]) < self.chunk_size * 3:
                chunks[-1] = chunks[-2] + chunks.pop()

            return chunks

        while len(self.articles_covers) < self.titles_num:
            article_url = f'{self.host}/posts/{self.curr_post_id}'
            article_html = self.get_html(article_url)
            article_soup = BeautifulSoup(article_html.text, 'html.parser')

            self.curr_post_id -= 1

            author = get_author(article_soup)
            title = get_title(article_soup)

            if not author:
                if not title:
                    continue

                author = 'Нет автора'

            content = get_content(article_soup, self.chunk_size)

            self.articles_covers.append((author, title))
            self.articles_content[article_url] = content

    def get_articles_content(self, article_id):
        self.curr_url = list(self.articles_content)[article_id - 1]
        self.articles_content[self.curr_url] = list(filter(None, self.articles_content[self.curr_url]))

        return self.articles_content[self.curr_url]

    def delete_paragraph(self, paragraph_id):
        curr_article = self.articles_content[self.curr_url]

        curr_article[paragraph_id - 1] = None

        if not any(curr_article):
            del self.articles_content[self.curr_url], self.articles_covers[paragraph_id - 1]

            self.get_content()

            return True

    @staticmethod
    def get_last_article(soup):
        items = soup.find('a', class_='card__link').get('href')
        last_post = int(items.replace('/posts/', ''))

        return last_post

    @staticmethod
    def get_html(url):
        return requests.get(url)
