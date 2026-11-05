"""Точка входа в приложение."""
from kivy.config import Config

# Размер окна как у мобильного телефона
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'position', 'auto')
Config.write()

from kivy.core.window import Window
from ui import WarehouseApp

if __name__ == "__main__":
    app = WarehouseApp()
    app.run()