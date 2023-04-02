from itertools import chain, islice
from bs4 import BeautifulSoup, Tag
import requests
import time

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.415'
}


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
        self.chunk_size = 45

        self.update_articles()

    def update_articles(self):
        lapse = time.time() - self.timer

        if lapse >= self.update_interval:
            self.get_content(50, self.num_articles_to_parse)
            self.timer = time.time()

        return self.articles_covers

    def get_content(self, attempts_num, titles_num):
        def get_last_article(soup):
            items = soup.find('a', class_='card__link').get('href')
            last_post = int(items.replace('/posts/', ''))

            return last_post

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

        main_page_html = self.get_html(self.host)
        main_page_soup = BeautifulSoup(main_page_html.text, 'html.parser')
        last_post_id = get_last_article(main_page_soup)

        self.articles_covers = []
        self.articles_content = {}

        while attempts_num and len(self.articles_covers) < titles_num:
            attempts_num -= 1

            article_url = f'{self.host}/posts/{last_post_id - attempts_num}'
            article_html = self.get_html(article_url)
            article_soup = BeautifulSoup(article_html.text, 'html.parser')

            author = get_author(article_soup)
            title = get_title(article_soup)

            if not author:
                if not title:
                    continue

                author = 'Нет автора'

            content = get_content(article_soup, self.chunk_size)

            self.articles_covers.append((author, title))
            self.articles_content[article_url] = content

    def get_articles_content(self, button_id):
        article_url = list(self.articles_content)[button_id - 1]

        return self.articles_content[article_url]

    @staticmethod
    def get_html(url):
        return requests.get(url, headers=HEADERS)
