# LMS Backend (Django + DRF)

Backend-часть учебной LMS-системы.  
Позволяет управлять курсами и уроками через REST API.

---

## Стек технологий
- Python 3.12+
- Django 5.2.5
- Django REST Framework 3.16.1
- PostgreSQL
- Pillow (работа с изображениями)
- python-dotenv

---

## Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>
```

### 2. Создать и активировать виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения
Создайте файл `.env` в корне проекта:
```
DEBUG=True
NAME=<db_name>
USER=<db_user>
PASSWORD=<db_password>
HOST=localhost
PORT=5432
```

### 5. Применить миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Создать суперпользователя
```bash
python manage.py createsuperuser
```
или использовать готовую команду:
```bash
python manage.py create_superuser
```
(создаст admin@admin.com / admin)

### 7. Запустить сервер
```bash
python manage.py runserver
```

---

## API эндпоинты

### Курсы
| Метод | URL | Описание |
|-------|-----|----------|
| GET   | `/api/courses/` | Список курсов |
| POST  | `/api/courses/` | Создать курс |
| GET   | `/api/courses/{id}/` | Получить курс |
| PUT/PATCH | `/api/courses/{id}/` | Изменить курс |
| DELETE| `/api/courses/{id}/` | Удалить курс |

### Уроки
| Метод | URL | Описание |
|-------|-----|----------|
| GET   | `/api/lessons/` | Список уроков |
| POST  | `/api/lessons/` | Создать урок |
| GET   | `/api/lessons/{id}/` | Получить урок |
| PUT/PATCH | `/api/lessons/{id}/` | Изменить урок |
| DELETE| `/api/lessons/{id}/` | Удалить урок |

---

## Модели

### Пользователь (`users.User`)
- email (логин)
- phone
- city
- avatar

### Курс (`lms.Course`)
- title
- preview
- description

### Урок (`lms.Lesson`)
- course (FK → Course)
- title
- description
- preview
- video_url

---

## Медиафайлы
Изображения курсов и уроков загружаются в `/media/`.
