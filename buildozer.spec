[app]
# Название приложения
title = Складской учёт

# Уникальное имя пакета и домен
package.name = warehouse
package.domain = org.baranskiy.warehouse

# Где лежат исходники
source.dir = .

# Какие файлы включать в сборку
# Добавил json, так как он часто нужен для конфигов или данных
source.include_exts = py,png,jpg,kv,atlas,db,json

# Исключаем папки, которые НЕ должны попасть в APK
# ВАЖНО: Убрал 'database' из исключений, если там есть connection.py для Android!
# Если database/connection.py универсален - оставь как есть. 
# Если там только серверный код - верни 'database' обратно.
source.exclude_dirs = api, migrations, __pycache__, tests, .git, .buildozer, venv

# Версия приложения
version = 1.0.0

# --- КРИТИЧЕСКИ ВАЖНЫЕ НАСТРОЙКИ (сохранены из твоего примера) ---
# Библиотеки: адаптированы под складской учет + PostgreSQL через CFFI
requirements = python3==3.10.12,hostpython3==3.10.12,setuptools,wheel,kivy==2.2.1,sqlalchemy,psycopg2cffi,cffi

# Ориентация экрана
orientation = portrait

# Собираем только под 64-битную архитектуру
android.archs = arm64-v8a

# Разрешения: Интернет (для БД) + Хранение (для логов/кэша)
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Версии API и NDK
android.api = 33
android.minapi = 21
android.ndk = 25b

# Автоматически принимаем лицензии SDK
android.accept_sdk_license = True

# Отключаем лишнюю оптимизацию Python (ускоряет сборку)
android.no_compile_pyo = True

# Формат артефакта (APK)
android.release_artifact = apk

# Обход ошибки libthorvg в сборщике
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
