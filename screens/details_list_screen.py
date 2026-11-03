"""Экран списка деталей с поиском."""
from __future__ import annotations

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from database.connection import get_session
from business.services import DetailService

KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<DetailsListScreen>:
    name: 'details_list'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: get_color_from_hex('#FAFAFA')
            Rectangle:
                pos: self.pos
                size: self.size

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
                text: 'Детали'
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

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(15), dp(10)]

            TextInput:
                id: search_input
                hint_text: 'Поиск...'
                multiline: False
                font_size: '14sp'
                background_color: get_color_from_hex('#FFFFFF')
                foreground_color: 0, 0, 0, 1
                cursor_color: 0.098, 0.463, 0.824, 1
                hint_text_color: 0.5, 0.5, 0.5, 1
                on_text: root.on_search()

        BoxLayout:
            id: add_button_box
            size_hint_y: None
            height: dp(50)
            padding: [dp(15), 0]

            Button:
                id: add_button
                text: '+ Добавить деталь'
                background_color: get_color_from_hex('#4CAF50')
                color: get_color_from_hex('#FFFFFF')
                font_size: '14sp'
                bold: True
                on_release: root.go_to_add()

        ScrollView:
            BoxLayout:
                id: details_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                padding: [dp(15), 0, dp(15), dp(15)]
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


class DetailsListScreen(Screen):
    def on_enter(self) -> None:
        user = getattr(App.get_running_app(), "current_user", None)
        can_edit = user and user.role.name in ['admin', 'manager']

        add_box = self.ids.get('add_button_box')
        if add_box:
            add_box.visible = can_edit

        self.load_details()

    def load_details(self, query: str = "") -> None:
        container = self.ids.details_container
        container.clear_widgets()

        try:
            session = get_session()
        
            service = DetailService(session)
            items = service.search(query=query)

            if not items:
                label = Label(
                    text="Детали не найдены",
                    size_hint_y=None,
                    height=dp(60),
                    font_size='14sp',
                    color=(0.3, 0.3, 0.3, 1),  # Тёмно-серый для читаемости
                )
                container.add_widget(label)
                return

            for detail in items:
                qty = f"{float(detail.quantity):g}"
                text = f"[b]{detail.sku}[/b]  {detail.name}\nОстаток: {qty} {detail.unit.short_name}"

                btn = Button(
                    text=text,
                    markup=True,
                    background_color=(1, 1, 1, 1),  # Чисто белый фон
                    color=(0, 0, 0, 1),             # Чисто чёрный текст
                    font_size='13sp',
                    halign='left',
                    valign='middle',
                    text_size=(None, None),
                    size_hint_y=None,
                    height=dp(60),
                    padding=[dp(15), dp(8)],
                    on_release=lambda instance, d=detail: self.go_to_detail(d.id),
                )

                with btn.canvas.before:
                    from kivy.graphics import Color, RoundedRectangle
                    Color(1, 1, 1, 1)
                    RoundedRectangle(pos=btn.pos, size=btn.size, radius=[6])

                container.add_widget(btn)

        except Exception as e:
            show_popup("Ошибка", str(e))
        finally:
            try:
                session.close()
            except NameError:
                pass
            except NameError:
                pass

    def on_search(self) -> None:
        query = self.ids.search_input.text.strip()
        self.load_details(query=query)

    def go_to_add(self) -> None:
        self.manager.current = "detail_form"
        self.manager.get_screen("detail_form").is_edit_mode = False
        self.manager.get_screen("detail_form").detail_id = None

    def go_to_detail(self, detail_id: int) -> None:
        self.manager.current = "detail_view"
        self.manager.get_screen("detail_view").detail_id = detail_id

    def go_back(self) -> None:
        self.manager.current = "main"