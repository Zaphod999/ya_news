import pytest

from django.urls import reverse

from http import HTTPStatus

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    """
    Главная страница, страница новости,
    страница регистрации пользователей
    и страницы входа в учетную запись и выхода из нее
    доступны анонимным пользователям
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment')),
    )
)
def test_comments_availability_for_author(author_client, name, args):
    """
    Страницы редактирования и удаления комментария
    доступны автору комментария
    """
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment')),
    )
)
def test_comments_redirect_for_anonimous_user(client, name, args):
    """
    При попытке перейти на страницу редактирования и удаления
    комментариев анонимный пользователь
    перенаправляется на страницу авторизации
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment')),
    )
)
def test_404_erorr_for_not_author(admin_client, name, args):
    """
    Авторизованный пользователь не может зайти на страницы
    редактирования или удаления чужих комментариев
    (возвращается ошибка 404).
    """
    url = reverse(name, args=args)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
