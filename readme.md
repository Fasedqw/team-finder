# TeamFinder — Вариант 1 (Избранное + фильтры участников)

Веб-приложение для поиска команды на pet-проекты. Бэкенд на Django, база данных PostgreSQL, запуск через Docker.

## Стек

- Python 3.12+
- Django 5.2
- PostgreSQL 16
- Docker / Docker Compose

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Fasedqw/team-finder.git
cd team-finder
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. Настроить переменные окружения

```bash
cp .env_example .env
```

Заполнить `.env`:

```
DJANGO_SECRET_KEY=ваш-секретный-ключ
DJANGO_DEBUG=True
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
TASK_VERSION=1
```

### 4. Запустить базу данных

```bash
docker compose up -d
```

### 5. Применить миграции и загрузить тестовые данные

```bash
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
```

### 6. Запустить сервер

```bash
python manage.py runserver
```

Сайт доступен на [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Тестовые аккаунты

| Email | Пароль |
|---|---|
| maria@yandex.ru | password |
| ivan@yandex.ru | password |
| olga@yandex.ru | password |

## Запуск тестов

```bash
python manage.py test
```

## Функциональность

- Регистрация и вход по email, автоматическая генерация аватарки
- Список проектов с пагинацией
- Создание, редактирование, завершение и удаление проектов
- Добавление проектов в избранное
- Участие в проектах
- Страница участников с 4 фильтрами:
  - Авторы избранных проектов
  - Авторы проектов, в которых я участвую
  - Пользователи, которым нравятся мои проекты
  - Участники моих проектов
- Редактирование профиля (аватар, контакты, GitHub)
- Смена пароля
- Админка с блокировкой/разблокировкой пользователей (`/admin/`)

## Автор

Бердников Константин Алексеевич — [github.com/Fasedqw](https://github.com/Fasedqw)
