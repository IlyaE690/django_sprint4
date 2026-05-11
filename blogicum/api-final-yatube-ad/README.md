# API для Yatube

## Описание
API для социальной сети Yatube. Позволяет создавать посты, комментарии, группы и подписываться на авторов.

## Технологии
- Python 3.13
- Django 4.2
- Django REST Framework
- Simple JWT
- Djoser

## Установка и запуск

1. Клонировать репозиторий
2. Установить зависимости:
pip install -r requirements.txt

3. Выполнить миграции:
python manage.py migrate

4. Запустить сервер:
python manage.py runserver

## Эндпоинты

- `/api/v1/posts/` — посты
- `/api/v1/groups/` — группы
- `/api/v1/posts/{post_id}/comments/` — комментарии
- `/api/v1/follow/` — подписки
- `/api/v1/jwt/create/` — получить JWT-токен

## Документация

После запуска сервера документация доступна по адресу:
http://127.0.0.1:8000/redoc/
