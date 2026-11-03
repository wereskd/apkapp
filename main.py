"""Точка входа в приложение.

Логи пишутся в app_log.txt во внутренней папке приложения, чтобы можно было
диагностировать вылеты без подключения телефона по adb.
"""
import os
import sys
import traceback


def _log_path():
    """Куда писать лог: на Android — во внутреннюю директорию приложения."""
    if 'ANDROID_ARGUMENT' in os.environ:
        from kivy.utils import platform  # noqa: F401
        app_dir = os.environ.get('ANDROID_PRIVATE', '.')
    else:
        app_dir = '.'
    return os.path.join(app_dir, 'app_log.txt')


def startup_logging(func):
    """Обёртка: любое исключение при запуске пишем в лог и показываем."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            err = traceback.format_exc()
            try:
                with open(_log_path(), 'w', encoding='utf-8') as f:
                    f.write(err)
            except OSError:
                pass
            print("STARTUP ERROR:\n" + err, file=sys.stderr)
            raise
    return wrapper


# Пишем метку самого раннего старта — если лога нет, приложение упало
# ещё до импорта Kivy.
try:
    with open(_log_path(), 'w', encoding='utf-8') as _f:
        _f.write("startup: importing modules...\n")
except OSError:
    pass

from kivy.config import Config

# Размер окна как у мобильного телефона (на Android игнорируется)
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'position', 'auto')

# На десктопе Config.write() может не иметь прав на запись — не критично
try:
    Config.write()
except OSError:
    pass

try:
    with open(_log_path(), 'a', encoding='utf-8') as _f:
        _f.write("kivy config ok; importing ui...\n")
except OSError:
    pass

from ui import WarehouseApp


@startup_logging
def main():
    app = WarehouseApp()
    app.run()


if __name__ == "__main__":
    main()
