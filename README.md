## Проект YamDB

### О проекте:

    Проект Yamdb собирает отзывы пользователей на различные произведения.

### Используемые технологии:
- Python
- Django
- Django Rest Framework
- Docker
- Postgres

### Заполнение .env файла:
В директории infra_sp2/infra/ необходимо создать файл .env и указать следующие значения:

- SECRET_KEY
- SERVERNAMES
- DB_ENGINE
- DB_NAME
- POSTGRES_USER
- POSTGRES_PASSWORD
- DB_HOST
- DB_PORT

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

### Автор:
Марина
