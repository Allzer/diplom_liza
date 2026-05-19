# ЦФП «Динамика» — веб-сайт центра физической подготовки

Дипломный проект: веб-приложение центра физической подготовки на **Python, FastAPI, PostgreSQL, HTML, CSS, Jinja2**.

## Возможности сайта

- Главная страница с описанием центра и преимуществами
- Раздел «О центре»
- Каталог **спортивных секций** с расписанием и ценами
- **Галерея** тренировочного процесса
- **Онлайн-запись** в секцию (форма → PostgreSQL)
- **Отзывы** пользователей с оценкой
- Страница контактов
- REST API клиентов: `/clients/`

## Запуск

1. Создайте виртуальное окружение и установите зависимости:

```bash
pip install -r requirements.txt
```

2. Настройте `.env` (пример):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=diplom_cfp
DB_USER=postgres
DB_PASS=your_password
```

3. Создайте БД и примените миграции:

```bash
python create_db.py
alembic upgrade head
```

4. Запустите сервер:

```bash
python run.py
```

Сайт: http://localhost:8000

## Структура

```
templates/     — HTML-шаблоны (Jinja2)
static/        — CSS и JS
src/web/       — маршруты веб-интерфейса
src/models/    — модели SQLAlchemy
src/api/       — REST API
```
