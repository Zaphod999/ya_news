import pytest

from news.models import News, Comment


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news_sample():
    news_sample = News.objects.create(  # Создаём объект заметки.
        title='Заголовок новости',
        text='Текст новости',
    )
    return news_sample


@pytest.fixture
def id_for_args(news_sample):
    return news_sample.id,


@pytest.fixture
def comment_sample(author, news_sample):
    comment_sample = Comment.objects.create(
        news=news_sample,
        author=author,
        text='Текст комментария',
    )
    return comment_sample


@pytest.fixture
def id_for_comment(comment_sample):
    return comment_sample.id,
