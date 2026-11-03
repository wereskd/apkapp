"""Экран регистрации пользователя."""
from __future__ import annotations

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from database.connection import get_session
from business.services import AuthService

KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<RegisterScreen>:
    name: 'register'
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
                text: 'Регистрация'
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
                on_release: root.go_to_login()

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: [dp(20), dp(15)]
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height

                Label:
                    text: 'Логин'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: reg_username
                    hint_text: 'Придумайте логин'
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    text: 'Пароль'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: reg_password
                    password: True
                    hint_text: 'Придумайте пароль'
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    text: 'ФИО'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: reg_fullname
                    hint_text: 'Иванов Иван Иванович'
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    text: 'Роль'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                # ИСПРАВЛЕНО: только manager и observer (admin создаёт только admin)
                Spinner:
                    id: reg_role_spinner
                    text: 'manager'
                    values: ['manager', 'observer']
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    color: 0, 0, 0, 1

                Label:
                    id: reg_error_label
                    text: ''
                    color: get_color_from_hex('#F44336')
                    font_size: '13sp'
                    size_hint_y: None
                    height: dp(25)

                Button:
                    text: 'Зарегистрироваться'
                    background_color: get_color_from_hex('#1976D2')
                    color: get_color_from_hex('#FFFFFF')
                    font_size: '15sp'
                    bold: True
                    size_hint_y: None
                    height: dp(45)
                    on_release: root.do_register()
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


class RegisterScreen(Screen):
    def do_register(self) -> None:
        username = self.ids.reg_username.text.strip()
        password = self.ids.reg_password.text.strip()
        fullname = self.ids.reg_fullname.text.strip()
        role_name = self.ids.reg_role_spinner.text
        error = self.ids.reg_error_label

        if not all([username, password, fullname]):
            error.text = "Заполните все поля"
            return

        try:
            session = get_session()
        
            auth = AuthService(session)
            auth.register(username, password, fullname, role_name, current_user=None)
            session.commit()
            error.text = ""
            show_popup("Успех", "Регистрация успешна! Теперь войдите.")
            self.manager.current = "login"
        except ValueError as e:
            error.text = str(e)
            try:
                session.rollback()
            except NameError:
                pass
        except Exception as e:
            error.text = f"Ошибка: {e}"
            try:
                session.rollback()
            except NameError:
                pass
        finally:
            try:
                session.close()
            except NameError:
                pass
            except NameError:
                pass

    def go_to_login(self) -> None:
        self.manager.current = "login"