![example workflow](https://github.com/margoloko/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## Проект YamDB

### О проекте:

Проект Yamdb собирает отзывы пользователей на различные произведения.
Это база с отзывами о фильмах, книгах и музыке. Пользователи могут оставлять рецензии на произведения, а также комментировать рецензии других.

    Проект доступен по адресу: 
    ``` http://84.201.160.207/api/v1/ ```
    Документация:
    ``` http://84.201.160.207/redoc/ ```

### Используемые технологии:
- Python
- Django
- Django Rest Framework
- Docker
- Postgres
-- -
### Заполнение .env файла:

- SECRET_KEY
- DB_ENGINE=django.db.backends.postgresql
- DB_NAME=postgres
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- DB_HOST=db
- DB_PORT=5432
-- -
### Для запуска приложения в контейнерах:
- Установите Docker
- Клонируйте репозиторий
``` git clone https://github.com/margoloko/infra_sp2.git ```
- Запустите docker-compose в директории infra_sp2/infra командой
``` docker-compose up -d --build ```
- Выполните миграции
``` docker-compose exec web python manage.py migrate ```
- Создайте суперпользователя
``` docker-compose exec web python manage.py createsuperuser ```
- Для сбора статики воспользуйтесь командой
``` docker-compose exec web python manage.py collectstatic --no-input ```
-- -
### Автор:
Марина
