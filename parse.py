from itertools import islice
from bs4 import BeautifulSoup, Tag
import requests
import time
from data.articles import Article
from data.paragraph import Paragraph


def batched(iterable, n):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield ' '.join(piece)
        piece = list(islice(i, n))


class ParseApp:
    update_interval = 86400

    def __init__(self, host: str, titles_num: int, session):
        self.host = host
        self.titles_num = titles_num
        self.session = session

        self.timer = 0
        self.chunk_size = 30

        self.update_articles()

    def update_articles(self):
        lapse = time.time() - self.timer

        if lapse >= self.update_interval:
            main_page_html = self.get_html(self.host)
            main_page_soup = BeautifulSoup(main_page_html.text, 'html.parser')
            self.curr_post_id = self.get_last_article(main_page_soup)

            self.clear_db()
            self.masks_lengths = []

            self.get_content()
            self.timer = time.time()

    def get_content(self, articles_added=0):
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

        while articles_added < self.titles_num:
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

            self.masks_lengths.append(len(content))

            article_cover = Article(title=title, author=author)
            self.session.add(article_cover)
            self.session.commit()

            for i, paragraph in enumerate(content):
                self.session.add(Paragraph(article_id=article_cover.id, num=i + 1, text=paragraph))

            self.session.commit()
            articles_added += 1

    def clear_db(self):
        self.session.query(Paragraph).delete()
        self.session.query(Article).delete()

        self.session.commit()

    def load_articles_covers(self):
        return self.session.query(Article.author, Article.title).all()

    def get_articles_content(self, article_id):
        self.curr_article = self.session.query(Article).get(article_id)

        self.article_text_chunks = list(map(str, self.curr_article.paragraphs))

        return self.article_text_chunks

    def delete_paragraph(self, paragraph_id):
        index = paragraph_id - 1
        self.article_text_chunks[index] = None
        shift = self.article_text_chunks[:index].count(None)

        self.session.delete(self.curr_article.paragraphs[index - shift])
        self.session.commit()

    @staticmethod
    def get_last_article(soup):
        items = soup.find('a', class_='card__link').get('href')
        last_post = int(items.replace('/posts/', ''))

        return last_post

    @staticmethod
    def get_html(url):
        return requests.get(url)
