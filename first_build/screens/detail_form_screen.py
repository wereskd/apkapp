"""Экран формы для добавления и редактирования детали."""
from __future__ import annotations

from decimal import Decimal
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from database.connection import get_session
from business.services import DetailService

KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<DetailFormScreen>:
    name: 'detail_form'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: get_color_from_hex('#FAFAFA')
            Rectangle:
                pos: self.pos
                size: self.size

        # Шапка
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(15), 0]
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#1976D2')
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                id: form_title_label
                text: root.form_title
                font_size: '18sp'
                bold: True
                color: get_color_from_hex('#FFFFFF')
                halign: 'left'

            Button:
                text: 'Назад'
                size_hint_x: None
                width: dp(80)
                background_color: get_color_from_hex('#1565C0')
                color: get_color_from_hex('#FFFFFF')
                font_size: '14sp'
                on_release: root.go_back()

        # Форма
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: [dp(20), dp(15)]
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height

                Label:
                    text: 'Артикул'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: sku_input
                    hint_text: 'Например: SKU-001'
                    multiline: False
                    readonly: root.is_edit_mode
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    text: 'Название'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: name_input
                    hint_text: 'Название детали'
                    multiline: False
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    text: 'Категория'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: category_input
                    hint_text: 'Например: Электроника'
                    multiline: False
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    text: 'Единица измерения'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: unit_input
                    hint_text: 'шт / кг / м / л'
                    multiline: False
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    text: 'Минимальный остаток'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: min_qty_input
                    hint_text: '0'
                    multiline: False
                    input_filter: 'float'
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    id: error_label
                    text: ''
                    color: get_color_from_hex('#F44336')
                    font_size: '13sp'
                    size_hint_y: None
                    height: dp(25)

                Button:
                    text: 'Сохранить'
                    background_color: get_color_from_hex('#1976D2')
                    color: get_color_from_hex('#FFFFFF')
                    font_size: '15sp'
                    bold: True
                    size_hint_y: None
                    height: dp(45)
                    on_release: root.save_detail()
"""

Builder.load_string(KV)


def show_popup(title: str, message: str) -> None:
    popup = Popup(
        title=title,
        content=Label(text=message, font_size='16sp'),
        size_hint=(0.9, 0.3),
        auto_dismiss=True,
    )
    popup.open()


class DetailFormScreen(Screen):
    """Экран формы для добавления/редактирования детали."""

    form_title = StringProperty("Добавить деталь")
    is_edit_mode = False
    # ИСПРАВЛЕНО: добавлен allownone=True для режима создания новой детали
    detail_id = NumericProperty(None, allownone=True) 

    def on_enter(self) -> None:
        if self.is_edit_mode and self.detail_id is not None:
            self.load_detail_data()
        else:
            self.clear_form()

    def load_detail_data(self) -> None:
        session = get_session()
        try:
            service = DetailService(session)
            detail = service.details.get(self.detail_id)
            if detail:
                self.ids.sku_input.text = detail.sku
                self.ids.name_input.text = detail.name
                self.ids.category_input.text = detail.category.name
                self.ids.unit_input.text = detail.unit.short_name
                self.ids.min_qty_input.text = str(detail.min_quantity)
                self.form_title = f"Редактировать: {detail.sku}"
        except Exception as e:
            show_popup("Ошибка", str(e))
        finally:
            session.close()

    def clear_form(self) -> None:
        self.ids.sku_input.text = ""
        self.ids.name_input.text = ""
        self.ids.category_input.text = ""
        self.ids.unit_input.text = ""
        self.ids.min_qty_input.text = "0"
        self.ids.error_label.text = ""
        self.form_title = "Добавить деталь"
        self.is_edit_mode = False
        self.detail_id = None

    def save_detail(self) -> None:
        """Сохраняет деталь с проверкой прав."""
        user = getattr(App.get_running_app(), "current_user", None)
        if not user or user.role.name not in ['admin', 'manager']:
            show_popup("Ошибка", "У вас нет прав для изменения деталей")
            return

        sku = self.ids.sku_input.text.strip()
        name = self.ids.name_input.text.strip()
        category = self.ids.category_input.text.strip()
        unit = self.ids.unit_input.text.strip()
        min_qty_str = self.ids.min_qty_input.text.strip()
        error = self.ids.error_label

        if not all([sku, name, category, unit]):
            error.text = "Заполните все обязательные поля"
            return

        try:
            min_qty = Decimal(min_qty_str) if min_qty_str else Decimal("0")
        except Exception:
            error.text = "Неверный формат минимального остатка"
            return

        session = get_session()
        try:
            service = DetailService(session, user=user)

            if self.is_edit_mode and self.detail_id is not None:
                service.update(
                    self.detail_id,
                    name=name,
                    min_quantity=min_qty,
                )
                session.commit()
                show_popup("Успех", "Деталь обновлена!")
            else:
                service.create(
                    sku=sku,
                    name=name,
                    category_name=category,
                    unit_short=unit,
                    min_quantity=min_qty,
                )
                session.commit()
                show_popup("Успех", "Деталь добавлена!")

            self.go_back()

        except ValueError as e:
            error.text = str(e)
            session.rollback()
        except Exception as e:
            error.text = f"Ошибка: {e}"
            session.rollback()
        finally:
            session.close()

    def go_back(self) -> None:
        self.manager.current = "details_list"