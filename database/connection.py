"""Подключение к базе данных (адаптивно для ПК и Android)."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import URL
from domain.entities import Base

# 1. Определяем, запущено ли приложение на Android
IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ

# 2. Настройки подключения
DB_USER = "postgres"
DB_PASSWORD = "123"  # ⚠️ ЗАМЕНИТЕ на ваш реальный пароль от PostgreSQL
DB_NAME = "warehouse"
DB_PORT = "5432"

if IS_ANDROID:
    # ⚠️ КРИТИЧЕСКИ ВАЖНО для Android:
    # Здесь ДОЛЖЕН быть IP-адрес вашего компьютера в локальной сети Wi-Fi (например, '192.168.1.15').
    # 'localhost' или '127.0.0.1' НЕ РАБОТАЮТ на телефоне, так как телефон будет искать базу внутри себя.
    # Чтобы узнать IP на Windows: откройте командную строку и введите 'ipconfig', найдите IPv4-адрес.
    DB_HOST = "10.51.3.52"  # <-- ЗАМЕНИТЕ '192.168.1.X' на реальный IP вашего ПК
    
    # Используем psycopg2cffi, так как он успешно компилируется под Android через Buildozer
    DRIVER = "postgresql+psycopg2cffi"
    
    # Регистрируем совместимость psycopg2cffi с обычным psycopg2 для SQLAlchemy
    try:
        import psycopg2cffi
        from psycopg2cffi import compat
        compat.register()
    except ImportError:
        pass
else:
    # На компьютере используем стандартный localhost и драйвер psycopg2
    DB_HOST = "localhost"
    DRIVER = "postgresql+psycopg2"

# 3. Формируем URL подключения
database_url = URL.create(
    drivername=DRIVER,
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# 4. Создаем движок SQLAlchemy
# echo=True можно включить для отладки SQL-запросов в консоли
engine = create_engine(database_url, echo=False)

# 5. Создаем фабрику сессий
SessionLocal = scoped_session(sessionmaker(bind=engine))

def get_session():
    """Получить новую сессию базы данных."""
    return SessionLocal()

def init_db():
    """Создать все таблицы, если они еще не существуют."""
    Base.metadata.create_all(bind=engine)

# Автоматическая инициализация таблиц при импорте модуля
init_db()
