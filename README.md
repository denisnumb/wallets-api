## Выбранный стек:

- REST API — `FastAPI`
- База Данных — `PostgreSQL`
- Миграции — `Alembic`
- СУБД — `SQLAlchemy`
- Тестирование — `Pytest`

## Пункты задания:

- [x] `POST api/v1/wallets/<WALLET_UUID>/operation`
- [x] `GET api/v1/wallets/{WALLET_UUID}`
- [x] Миграции для БД
- [x] Обработка параллельных запросов
- [x] Приложение и БД запускаются в Docker-контейнере, среда поднимается с помощью docker-compose
- [x] Эндпоинты покрыты тестами (`/app/tests/test_api.py`)