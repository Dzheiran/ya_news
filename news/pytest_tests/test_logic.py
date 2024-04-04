import pytest

from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news_id_for_args, form_data
):
    """Тестирование невозможности создания комментария анонимом."""
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, author, news_id_for_args, form_data
):
    """Тестирование создания заметки залогиненым пользователем."""
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, news_id_for_args, form_data):
    """Тестирование использования плохих слов."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client, comment_id_for_args, news_id_for_args
):
    """Тестирование удаления комментария автором."""
    url = reverse('news:delete', args=comment_id_for_args)
    redirect_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.delete(url)
    assertRedirects(response, f'{redirect_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_id_for_args, comment
):
    """Тестирование невозможности удаления комментария неавтором."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client,
        news_id_for_args,
        comment_id_for_args,
        form_data,
        comment
):
    """Тестирование редактирования комментария автором."""
    url = reverse('news:edit', args=comment_id_for_args)
    redirect_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{redirect_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        comment_id_for_args,
        form_data,
        comment
):
    """Тестирование невозможности редактирования комментария неавтором."""
    url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_form_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_form_db.text
