from pytest_django.asserts import assertRedirects

from django.urls import reverse

from news.models import Comment

from news.forms import BAD_WORDS, WARNING

from django.core.exceptions import ValidationError

from http import HTTPStatus

import pytest


def test_logged_in_user_can_create_comment(
        author_client,
        author,
        form_data,
        id_for_args,
        ):
    url = reverse('news:detail', args=id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonimous_user_cannot_create_comment(
        client,
        form_data,
        id_for_args,
        ):
    url = reverse('news:detail', args=id_for_args)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_comment_with_bad_words_is_not_published(author_client, id_for_args):
    bad_words_data = {'text': f'Ты {BAD_WORDS[0]}, Израэль Хенкс'}
    url = reverse('news:detail', args=id_for_args)
    author_client.post(url, data=bad_words_data)
    assert Comment.objects.count() == 0
    assert ValidationError(WARNING)


def test_author_can_edit_his_comment(
        author_client, form_data, comment_sample, id_for_args
        ):
    # Получаем адрес страницы редактирования заметки:
    url = reverse('news:edit', args=id_for_args)
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(url, data=form_data)
    # Проверяем редирект:
    assertRedirects(
        response, f'{reverse("news:detail", args=id_for_args)}#comments'
        )
    # Обновляем объект заметки note: получаем обновлённые данные из БД:
    comment_sample.refresh_from_db()
    # Проверяем, что атрибуты заметки соответствуют обновлённым:
    assert comment_sample.text == form_data['text']


def test_other_user_cant_edit_comment(
        admin_client, form_data, comment_sample, id_for_args
        ):
    url = reverse('news:edit', args=id_for_args)
    response = admin_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(id=comment_sample.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment_sample.text == comment_from_db.text


def test_author_can_delete_comment(author_client, id_for_args, comment_sample):
    url = reverse('news:delete', args=id_for_args)
    response = author_client.post(url)
    assertRedirects(
        response, f'{reverse("news:detail", args=id_for_args)}#comments'
        )
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(
        admin_client, id_for_args, comment_sample
        ):
    url = reverse('news:delete', args=id_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
