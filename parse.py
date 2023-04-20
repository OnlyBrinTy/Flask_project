from itertools import islice
from bs4 import BeautifulSoup, Tag
import requests
import time
from data.articles import Article
from data.paragraph import Paragraph
from data.mask import Mask
from data.users import User


def batched(iterable, n):   # аналог batched из itertools для python 3.12
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield ' '.join(piece)
        piece = list(islice(i, n))


class ParseApp:
    update_interval = 86400  # интервал для обновления статей в БД

    def __init__(self, host: str, titles_num: int, session):
        self.host = host
        self.titles_num = titles_num
        self.session = session

        self.timer = 0
        self.chunk_size = 30  # кол-во слов в каждом абзаце

        self.update_articles()

    def update_articles(self):
        lapse = time.time() - self.timer

        if lapse >= self.update_interval:
            main_page_html = self.get_html(self.host)
            main_page_soup = BeautifulSoup(main_page_html.text, 'html.parser')
            # обновляем указатель номера(id) последней статьи
            self.curr_post_id = self.get_last_article(main_page_soup)

            self.clear_db()
            self.masks_lengths = []  # кол-во абзацев для каждой статьи

            self.get_content()
            self.timer = time.time()

    def get_content(self, articles_added=0):
        """Здесь мы собираем информацию о статьях с сайта и заносим её в БД"""

        def get_author(soup):
            # получение автора статьи

            item = soup.find('div', class_='post-authors__name')
            author_name = item.text.strip() if item else None

            return author_name

        def get_title(soup):
            # получение заголовка статьи

            item = soup.find('h1', class_='post-title')
            title_name = item.text.replace('\xa0', ' ').strip() if item else None

            return title_name

        def get_content(soup, chunk_size):
            # получение текста статьи

            extra_classes = ('caption', 'credit')  # ненужные классы

            item = soup.find('div', class_='free-content')
            paragraphs = item.find_all('p', class_=lambda c: c not in extra_classes)

            words = ' '.join(map(Tag.get_text, paragraphs)).split()  # разбиение текста на слова
            chunks = list(batched(words, chunk_size))  # разбиение текста на куски по 30 слов
            if len(chunks[-1]) < self.chunk_size * 3:
                # добавляем текст последней статьи к предпоследней если в ней слишком мало слов
                chunks[-1] = chunks[-2] + chunks.pop()

            return chunks

        while articles_added < self.titles_num:  # пытаемся достать статьи пока не наберётся 10
            article_url = f'{self.host}/posts/{self.curr_post_id}'
            article_html = self.get_html(article_url)  # получаем html статьи
            article_soup = BeautifulSoup(article_html.text, 'html.parser')

            # двигаем указатель номера статьи на следующую статью
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
                # добавляем параграфы в отдельную таблицу, которая связана с таблицей articles
                self.session.add(Paragraph(article_id=article_cover.id, num=i + 1, text=paragraph))

            self.session.commit()
            articles_added += 1

    def clear_db(self):  # отчистка статей для добавления новых
        self.session.query(Paragraph).delete()
        self.session.query(Article).delete()

        self.session.commit()

    def load_articles_covers(self):  # забираем обложки статей с сервера
        return self.session.query(Article.author, Article.title).all()

    def get_articles_content(self, article_id):  # забираем тексты статей с сервера
        article = self.session.query(Article).get(article_id)
        article_text_chunks = list(map(str, article.paragraphs))

        return article_text_chunks

    @staticmethod
    def get_last_article(soup):  # получение id последней статьи
        items = soup.find('a', class_='card__link').get('href')
        last_post = int(items.replace('/posts/', ''))

        return last_post

    @staticmethod
    def get_html(url):
        return requests.get(url)
