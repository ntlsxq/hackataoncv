# CV Interview System

Система для роботи з резюме та проведення інтерв'ю з використанням AI.

## Опис проекту

Система дозволяє користувачам:
- Створювати та зберігати резюме з версійністю
- Отримувати оцінку резюме від AI
- Проводити інтерв'ю з AI-асистентом для підготовки до співбесід

## Технологічний стек

- **Backend**: FastAPI (Python 3.12+)
- **База даних**: PostgreSQL
- **ORM**: SQLAlchemy (async)
- **Аутентифікація**: JWT, Google OAuth
- **AI**: Google Gemini API
- **Міграції**: Alembic

## Структура даних

### Таблиці бази даних

#### `users`
Зберігає інформацію про користувачів:
- `id` (UUID) - унікальний ідентифікатор
- `name` (String) - ім'я користувача
- `email` (String) - email (унікальний)
- `password` (String, nullable) - хешований пароль (може бути NULL для OAuth користувачів)

#### `documents`
Зберігає документи (резюме) користувачів:
- `id` (UUID) - унікальний ідентифікатор
- `owner_id` (UUID, FK → users.id) - власник документа
- `current_version` (Integer) - поточна версія документа
- `created_at` (DateTime) - дата створення
- `updated_at` (DateTime) - дата останнього оновлення

#### `document_versions`
Зберігає версії документів:
- `id` (UUID) - унікальний ідентифікатор
- `document_id` (UUID, FK → documents.id, CASCADE) - документ
- `version_number` (Integer) - номер версії
- `content` (JSON) - вміст резюме у форматі JSON
- `created_at` (DateTime) - дата створення версії

#### `interview_chats`
Зберігає чати для інтерв'ю:
- `id` (UUID) - унікальний ідентифікатор
- `owner_id` (UUID, FK → users.id, CASCADE) - власник чату
- `title` (String, nullable) - назва чату
- `position` (String, nullable) - позиція для якої проводиться інтерв'ю
- `created_at` (DateTime) - дата створення
- `updated_at` (DateTime) - дата останнього оновлення

#### `interview_messages`
Зберігає повідомлення в чатах:
- `id` (UUID) - унікальний ідентифікатор
- `chat_id` (UUID, FK → interview_chats.id, CASCADE) - чат
- `role` (Enum: user/assistant/system) - роль відправника
- `content` (Text) - текст повідомлення
- `created_at` (DateTime) - дата створення

## Де зберігаються дані

Всі дані зберігаються в **PostgreSQL базі даних**.

### Локація бази даних

При запуску через Docker Compose:
- База даних: контейнер `cv-gen-postgres`
- Дані зберігаються в Docker volume `postgres-data`
- Шлях в контейнері: `/var/lib/postgresql/data`

### Підключення до бази даних

Параметри підключення налаштовуються через змінні оточення:
- `DATABASE_URL` - повний URL підключення до PostgreSQL

## Функціонал видалення даних користувача

### Видалення облікового запису користувача

**Ендпоінт**: `DELETE /api/auth/me`

**Авторизація**: Потрібен JWT токен (заголовок `Authorization: Bearer <token>`)

**Що видаляється автоматично (каскадно):**

1. **InterviewChat** - всі чати користувача видаляються через `ondelete="CASCADE"` в ForeignKey
2. **InterviewMessage** - всі повідомлення в чатах видаляються через `ondelete="CASCADE"` від InterviewChat

**Що НЕ видаляється автоматично:**

1. **Document** - документи користувача залишаються в базі даних (немає `ondelete="CASCADE"` в ForeignKey)
2. **DocumentVersion** - версії документів залишаються (видаляться тільки разом з документом)

**Важливо**: При видаленні користувача його документи (резюме) залишаються в системі. Для повного видалення всіх даних користувача необхідно спочатку видалити всі документи вручну через ендпоінт `DELETE /api/documents/{document_id}`.

### Видалення окремих даних

#### Видалення документа
**Ендпоінт**: `DELETE /api/documents/{document_id}`

При видаленні документа автоматично видаляються всі його версії через `ondelete="CASCADE"`.

#### Видалення чату інтерв'ю
**Ендпоінт**: `DELETE /api/interview/chats/{chat_id}`

При видаленні чату автоматично видаляються всі повідомлення в чаті через `ondelete="CASCADE"`.

## Як видалити всі дані користувача

### Повне видалення через API

1. Отримати список всіх документів: `GET /api/documents`
2. Видалити кожен документ: `DELETE /api/documents/{document_id}` для кожного документа
3. Видалити обліковий запис: `DELETE /api/auth/me`

### Видалення через базу даних

```sql
-- Видалити всі дані користувача (замініть USER_ID на реальний UUID)
BEGIN;

-- Видалити версії документів
DELETE FROM document_versions 
WHERE document_id IN (SELECT id FROM documents WHERE owner_id = 'USER_ID');

-- Видалити документи
DELETE FROM documents WHERE owner_id = 'USER_ID';

-- Видалити повідомлення (видаляться автоматично через CASCADE)
-- Видалити чати (видаляться автоматично через CASCADE)
-- Видалити користувача
DELETE FROM users WHERE id = 'USER_ID';

COMMIT;
```

### Видалення всіх даних системи

**Увага**: Це видалить всі дані всіх користувачів!

```sql
-- Очистити всі таблиці
TRUNCATE TABLE interview_messages CASCADE;
TRUNCATE TABLE interview_chats CASCADE;
TRUNCATE TABLE document_versions CASCADE;
TRUNCATE TABLE documents CASCADE;
TRUNCATE TABLE users CASCADE;
```

Або через Docker:

```bash
# Зупинити контейнери
docker-compose down

# Видалити volume з даними
docker volume rm hackataoncv_postgres-data

# Запустити знову
docker-compose up -d
```

## Запуск проекту

### Вимоги

- Python 3.12+
- PostgreSQL 15+
- Docker та Docker Compose (опціонально)

### Налаштування

1. Створіть файл `.env` в корені проекту:
```env
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/cv
API_HOST=0.0.0.0
API_PORT=8000
JWT_SECRET=your-secret-key-here
DOMAIN=http://localhost:8000
GOOGLE_AUTH_CLIENT_ID=your-google-client-id
GOOGLE_AUTH_SECRET=your-google-client-secret
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
```

2. Запустіть міграції:
```bash
alembic upgrade head
```

3. Запустіть сервер:
```bash
python main.py
```

### Запуск через Docker

```bash
docker-compose up -d
```

API буде доступне за адресою: `http://localhost:8000`

Документація API: `http://localhost:8000/api/docs`

## API Endpoints

### Аутентифікація
- `POST /api/auth/register` - реєстрація
- `POST /api/auth/login` - вхід
- `GET /api/auth/me` - інформація про поточного користувача
- `DELETE /api/auth/me` - видалення облікового запису
- `GET /api/auth/google/login` - вхід через Google OAuth

### Документи
- `GET /api/documents` - список документів користувача
- `POST /api/documents` - створення документа
- `GET /api/documents/{document_id}` - отримання документа
- `PUT /api/documents/{document_id}` - оновлення документа (створює нову версію)
- `GET /api/documents/{document_id}/versions/{version_number}` - отримання версії
- `DELETE /api/documents/{document_id}` - видалення документа

### Інтерв'ю
- `GET /api/interview/chats` - список чатів користувача
- `POST /api/interview/chats` - створення чату
- `GET /api/interview/chats/{chat_id}` - отримання чату з повідомленнями
- `DELETE /api/interview/chats/{chat_id}` - видалення чату
- `POST /api/interview/chats/{chat_id}/messages` - відправка повідомлення

## Безпека даних

- Паролі зберігаються у хешованому вигляді (bcrypt)
- Аутентифікація через JWT токени
- Підтримка OAuth через Google
- CORS налаштований для роботи з фронтендом

## Примітки

- При видаленні користувача його документи (резюме) залишаються в системі. Для повного видалення необхідно спочатку видалити всі документи.
- Версії документів зберігаються історію змін резюме.
- Повідомлення в чатах зберігаються для продовження розмови з AI.

