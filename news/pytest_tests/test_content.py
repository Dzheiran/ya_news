import pytest

from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, get_news_list):
    """Проверяем количество новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, get_news_list):
    """Проверяем сортировку новостей на главной странице от новой к старой."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news_id_for_args, get_cpmments_list):
    """Проверяем сортировку комментариев к новости от старой к новой."""
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    comments_list = get_cpmments_list
    comments_created = [comment.created for comment in comments_list]
    sorted_timestamps = sorted(comments_created)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_newspage_contains_form(
    news_id_for_args, parametrized_client, form_in_list
):
    """Тестирование наличия формы добавления комментария."""
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_list
    if 'form' in response.context:
        assert isinstance(response.context['form'], CommentForm)
