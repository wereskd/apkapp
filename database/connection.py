"""Подключение к базе данных (адаптивно для ПК и Android).

ВАЖНО: движок SQLAlchemy создаётся ЛЕНИВО (при первом обращении), а не при
импорте модуля. Если создать engine/инициализировать драйвер на импорте,
то любое исключение (недоступен PostgreSQL, нет драйвера) приведёт к
немедленному вылету приложения на старте. Теперь ошибки подключения
безопасно перехватываются в UI и показываются пользователю.
"""
import os

IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ

# 1. Настройки подключения
DB_USER = "postgres"
DB_PASSWORD = "123"  # ⚠️ ЗАМЕНИТЕ на ваш реальный пароль от PostgreSQL
DB_NAME = "warehouse"
DB_PORT = "5432"

if IS_ANDROID:
    # ⚠️ КРИТИЧЕСКИ ВАЖНО для Android:
    # Здесь ДОЛЖЕН быть IP-адрес вашего компьютера в локальной сети Wi-Fi.
    # 'localhost' или '127.0.0.1' НЕ РАБОТАЮТ на телефоне.
    DB_HOST = "10.51.3.52"  # <-- ЗАМЕНИТЕ на реальный IP вашего ПК
    DRIVER = "postgresql+pg8000"  # чистый Python — единственный рабочий драйвер в APK
else:
    DB_HOST = "localhost"
    try:
        import psycopg2  # noqa: F401
        DRIVER = "postgresql+psycopg2"
    except ImportError:
        DRIVER = "postgresql+pg8000"

_engine = None
_SessionLocal = None


def _make_url():
    from sqlalchemy.engine import URL
    return URL.create(
        drivername=DRIVER,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )


def get_engine():
    """Создать движок при первом обращении (ленивая инициализация)."""
    global _engine
    if _engine is None:
        from sqlalchemy import create_engine
        _engine = create_engine(_make_url(), echo=False, pool_pre_ping=True)
    return _engine


def get_session():
    """Получить новую сессию базы данных."""
    global _SessionLocal
    if _SessionLocal is None:
        from sqlalchemy.orm import sessionmaker, scoped_session
        _SessionLocal = scoped_session(sessionmaker(bind=get_engine()))
    return _SessionLocal()


def init_db():
    """Создать все таблицы, если они еще не существуют."""
    from domain.entities import Base
    Base.metadata.create_all(bind=get_engine())
