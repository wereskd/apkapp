"""Экран управления пользователями (только для admin)."""
from __future__ import annotations

from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from business.services import AuthService
from dal.repositories import UserRepository
from database.connection import get_session

KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<UsersScreen>:
    name: 'users'
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
                text: 'Пользователи'
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
            height: dp(50)
            padding: [dp(15), dp(10)]

            Button:
                text: '+ Добавить пользователя'
                background_color: get_color_from_hex('#4CAF50')
                color: get_color_from_hex('#FFFFFF')
                font_size: '14sp'
                bold: True
                on_release: root.show_add_user_popup()

        ScrollView:
            BoxLayout:
                id: users_container
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


class UsersScreen(Screen):
    """Экран управления пользователями."""

    def on_enter(self) -> None:
        user = getattr(App.get_running_app(), "current_user", None)
        if not user or user.role.name != 'admin':
            show_popup("Ошибка", "Доступ запрещён")
            self.manager.current = "main"
            return
        self.load_users()

    def load_users(self) -> None:
        container = self.ids.users_container
        container.clear_widgets()

        session = get_session()
        try:
            repo = UserRepository(session)
            users = repo.list()

            if not users:
                container.add_widget(Label(
                    text="Пользователи не найдены",
                    size_hint_y=None,
                    height=dp(60),
                    font_size='14sp',
                    color=(0.3, 0.3, 0.3, 1),
                ))
                return

            for user in users:
                text = f"[b]{user.username}[/b]  {user.full_name}\nРоль: {user.role.name}"

                btn = Button(
                    text=text,
                    markup=True,
                    background_color=(1, 1, 1, 1),
                    color=(0, 0, 0, 1),
                    font_size='13sp',
                    halign='left',
                    valign='middle',
                    text_size=(None, None),
                    size_hint_y=None,
                    height=dp(60),
                    padding=[dp(15), dp(8)],
                )

                with btn.canvas.before:
                    Color(1, 1, 1, 1)
                    RoundedRectangle(pos=btn.pos, size=btn.size, radius=[6])

                container.add_widget(btn)

        except Exception as e:
            show_popup("Ошибка", str(e))
        finally:
            session.close()

    def show_add_user_popup(self) -> None:
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))

        username_input = TextInput(
            hint_text='Логин',
            size_hint_y=None,
            height=dp(40),
            font_size='14sp',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
        )
        password_input = TextInput(
            hint_text='Пароль',
            password=True,
            size_hint_y=None,
            height=dp(40),
            font_size='14sp',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
        )
        fullname_input = TextInput(
            hint_text='ФИО',
            size_hint_y=None,
            height=dp(40),
            font_size='14sp',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
        )
        # ИСПРАВЛЕНО: только актуальные роли согласно ТЗ
        role_spinner = Spinner(
            text='manager',
            values=['admin', 'manager', 'observer'],
            size_hint_y=None,
            height=dp(40),
            font_size='14sp',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
        )

        content.add_widget(username_input)
        content.add_widget(password_input)
        content.add_widget(fullname_input)
        content.add_widget(role_spinner)

        buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        popup = Popup(
            title='Новый пользователь',
            content=content,
            size_hint=(0.9, 0.6),
            auto_dismiss=False,
        )

        def on_confirm():
            username = username_input.text.strip()
            password = password_input.text.strip()
            fullname = fullname_input.text.strip()
            role_name = role_spinner.text

            if not all([username, password, fullname]):
                show_popup("Ошибка", "Заполните все поля")
                return

            session = get_session()
            try:
                auth = AuthService(session)
                current_user = App.get_running_app().current_user
                auth.register(username, password, fullname, role_name, current_user=current_user)
                session.commit()
                popup.dismiss()
                show_popup("Успех", "Пользователь создан!")
                self.load_users()
            except ValueError as e:
                show_popup("Ошибка", str(e))
                session.rollback()
            except Exception as e:
                show_popup("Ошибка", str(e))
                session.rollback()
            finally:
                session.close()

        btn_confirm = Button(
            text='Создать',
            background_color=(0.098, 0.463, 0.824, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        btn_confirm.bind(on_release=lambda x: on_confirm())

        btn_cancel = Button(
            text='Отмена',
            background_color=(0.96, 0.96, 0.96, 1),
            color=(0.098, 0.463, 0.824, 1),
        )
        btn_cancel.bind(on_release=popup.dismiss)

        buttons.add_widget(btn_confirm)
        buttons.add_widget(btn_cancel)
        content.add_widget(buttons)

        popup.open()

    def go_back(self) -> None:
        self.manager.current = "main"