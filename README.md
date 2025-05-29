# 🧙‍♂️ DnD Character Generator

Это проект генератора персонажей для настольной ролевой игры Dungeons & Dragons (DnD).  
Он поддерживает:

- ✅ Регистрацию и вход пользователей
- ✅ Генерацию случайного персонажа с ASCII портретом
- ✅ Сохранение персонажей в PostgreSQL
- ✅ CLI-интерфейс
- ✅ REST API (FastAPI)

---

## 📦 Структура проекта

```
zachet1/
├── api_server.py          # FastAPI сервер
├── cli_app.py             # CLI интерфейс
├── character_logic.py     # Логика генерации персонажа
├── db.py                  # Подключение к базе
├── requirements.txt       # Зависимости
├── run_all.bat            # BAT-скрипт запуска сервера и CLI
├── data/
│   ├── races.json
│   ├── backgrounds.json
│   └── class/
│       ├── class-barbarian.json
│       ├── class-wizard.json
│       └── ...
```

---

## 🛠 Установка

1. Установи Python 3.10+
2. Создай виртуальное окружение:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Установи зависимости:

```bash
pip install -r requirements.txt
```

4. Настрой PostgreSQL и создай базу:

```sql
CREATE DATABASE dnd_gen;
```

5. Пропиши данные подключения в `db.py`:

```python
def get_connection():
    return psycopg2.connect(
        dbname="dnd_gen",
        user="postgres",
        password="your_password",
        host="127.0.0.1",
        port="5432"
    )
```

6. Создай таблицы:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name TEXT,
    race TEXT,
    class TEXT,
    background TEXT,
    subclass TEXT,
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    user_id INTEGER REFERENCES users(id),
    portrait TEXT,
    skills TEXT,
    features TEXT
);
```

---

## 🚀 Запуск

### Автоматический запуск сервера и CLI:

Просто запусти:

```
run_all.bat
```

### Вручную:

1. Запусти сервер:

```bash
uvicorn api_server:app --reload
```

2. В другой консоли запусти CLI:

```bash
python cli_app.py
```

---

## 📋 API Примеры

- `GET /characters/{user_id}` — список персонажей пользователя
- `POST /generate` — сгенерировать персонажа
- `GET /character/{id}` — получить подробности

---

## 🔧 Зависимости

```
fastapi
uvicorn
psycopg2
pydantic
colorama
requests
pywhatkit
duckduckgo-search
translate
Pillow
```

---

## 🧾 Лицензия

MIT License. Бесплатно для обучения и персонального использования.
