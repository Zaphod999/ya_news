import pytest

from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from news.models import News, Comment


@pytest.fixture
def news_list():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    News.objects.bulk_create(all_news)


@pytest.mark.django_db
def test_news_count(client, news_list):
    """
    Количество новостей на главной странице — не более 10.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.fixture
def comments_list(news_sample, author, id_for_args):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news_sample, author=author, text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


def test_comments_order(author_client, comments_list, id_for_args):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', args=id_for_args)
    response = author_client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_for_args):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    url = reverse('news:detail', args=id_for_args)
    response = client.get(url)
    assert 'form' not in response.context


def test_logged_in_client_has_form(author_client, id_for_args):
    """
    Авторизованному пользователю доступна форма для
    отправки комментария на странице отдельной новости.
    """
    url = reverse('news:detail', args=id_for_args)
    response = author_client.get(url)
    assert 'form' in response.context
