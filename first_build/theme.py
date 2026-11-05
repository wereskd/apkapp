"""Цветовая схема и стили приложения."""
from kivy.utils import get_color_from_hex

COLORS = {
    'primary': get_color_from_hex('#1976D2'),
    'primary_dark': get_color_from_hex('#1565C0'),
    'accent': get_color_from_hex('#FF9800'),
    'background': get_color_from_hex('#FAFAFA'),
    'surface': get_color_from_hex('#FFFFFF'),
    'text_primary': get_color_from_hex('#212121'),
    'text_secondary': get_color_from_hex('#757575'),
    'text_on_primary': get_color_from_hex('#FFFFFF'),
    'success': get_color_from_hex('#4CAF50'),
    'error': get_color_from_hex('#F44336'),
}

SIZES = {
    'button_height': 50,
    'input_height': 45,
    'card_padding': 20,
    'screen_padding': 30,
    'spacing': 15,
}