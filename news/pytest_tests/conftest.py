import pytest

from datetime import datetime, timedelta
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Пользователь (автор)."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Пользователь (неавтор)."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Залогиненный автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Залогиненный неавтор."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создаём новость."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    """Создаём комментарий."""
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news,
    )
    return comment

@pytest.fixture
def news_id_for_args(news):
    """Получаем id новости."""
    return (news.id,)

@pytest.fixture
def comment_id_for_args(comment):
    """Получаем id комментария."""
    return (comment.id,)


@pytest.fixture
def get_news_list():
    """Создаём много новостей."""
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def get_cpmments_list(author, news):
    """Создаём много комментариев."""
    now = timezone.now()
    cpmments_list = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment(
            text=f'Просто комментарий {index}',
            author=author,
            news=news
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        cpmments_list.append(comment)
    return cpmments_list
