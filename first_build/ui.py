"""Kivy UI: экран входа и главное меню."""
from __future__ import annotations

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput

from database.connection import get_session
from business.services import AuthService, DetailService
from register_screen import RegisterScreen
from screens.details_list_screen import DetailsListScreen
from screens.detail_form_screen import DetailFormScreen
from screens.detail_view_screen import DetailViewScreen
from screens.users_screen import UsersScreen
from screens.operation_screen import OperationScreen

KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<StyledTextInput>:
    size_hint_y: None
    height: dp(45)
    multiline: False
    padding: [dp(15), dp(10)]
    font_size: '16sp'
    background_color: get_color_from_hex('#F5F5F5')
    foreground_color: 0.13, 0.13, 0.13, 1
    cursor_color: 0.098, 0.463, 0.824, 1
    hint_text_color: 0.62, 0.62, 0.62, 1

<PrimaryButton>:
    background_color: get_color_from_hex('#1976D2')
    color: get_color_from_hex('#FFFFFF')
    font_size: '16sp'
    bold: True
    size_hint_y: None
    height: dp(50)

<SecondaryButton>:
    background_color: get_color_from_hex('#F5F5F5')
    color: get_color_from_hex('#1976D2')
    font_size: '16sp'
    size_hint_y: None
    height: dp(50)

<LoginScreen>:
    name: 'login'
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
            height: dp(200)
            orientation: 'vertical'
            spacing: dp(10)
            padding: [dp(40), dp(40), dp(40), 0]

            Label:
                text: 'Складской учёт'
                font_size: '28sp'
                bold: True
                color: get_color_from_hex('#1976D2')
                size_hint_y: None
                height: dp(50)

            Label:
                text: 'Войдите в систему'
                font_size: '16sp'
                color: get_color_from_hex('#757575')
                size_hint_y: None
                height: dp(30)

        BoxLayout:
            orientation: 'vertical'
            padding: [dp(40), 0, dp(40), dp(40)]
            spacing: dp(20)

            StyledTextInput:
                id: username
                hint_text: 'Логин'

            StyledTextInput:
                id: password
                hint_text: 'Пароль'
                password: True

            PrimaryButton:
                text: 'Войти'
                on_release: root.do_login()

            SecondaryButton:
                text: 'Создать аккаунт'
                on_release: root.go_to_register()

            Label:
                id: error_label
                text: ''
                color: get_color_from_hex('#F44336')
                font_size: '14sp'
                size_hint_y: None
                height: dp(30)

<MainScreen>:
    name: 'main'
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

            BoxLayout:
                orientation: 'vertical'
                padding: [dp(10), 0]

                Label:
                    text: 'Складской учёт'
                    font_size: '18sp'
                    bold: True
                    color: get_color_from_hex('#FFFFFF')
                    size_hint_y: None
                    height: dp(30)
                    halign: 'left'

                Label:
                    text: root.welcome_text
                    font_size: '11sp'
                    color: get_color_from_hex('#E3F2FD')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

            Button:
                text: 'Выйти'
                size_hint_x: None
                width: dp(80)
                background_color: get_color_from_hex('#1565C0')
                color: get_color_from_hex('#FFFFFF')
                font_size: '14sp'
                on_release: root.logout()

        ScrollView:
            BoxLayout:
                id: menu_container
                orientation: 'vertical'
                padding: dp(15)
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height
"""


class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.foreground_color = (0.13, 0.13, 0.13, 1)
        self.cursor_color = (0.098, 0.463, 0.824, 1)
        self.hint_text_color = (0.62, 0.62, 0.62, 1)


class PrimaryButton(Button):
    pass


class SecondaryButton(Button):
    pass


class LoginScreen(Screen):
    def do_login(self) -> None:
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        error = self.ids.error_label

        if not username or not password:
            error.text = "Введите логин и пароль"
            return

        session = get_session()
        try:
            auth = AuthService(session)
            user = auth.login(username, password)
            app = App.get_running_app()
            app.current_user = user
            app.current_session = session
            self.manager.current = "main"
            self.manager.get_screen("main").on_enter()
            error.text = ""
        except ValueError as e:
            error.text = str(e)
            session.close()
        except Exception as e:
            error.text = f"Ошибка: {e}"
            session.close()

    def go_to_register(self) -> None:
        self.manager.current = "register"


class MainScreen(Screen):
    welcome_text = StringProperty("")

    def on_enter(self) -> None:
        app = App.get_running_app()
        user = getattr(app, "current_user", None)
        if user:
            self.welcome_text = f"{user.full_name} • {user.role.name}"
            self._build_menu(user.role.name)

    def _build_menu(self, role_name: str):
        container = self.ids.menu_container
        container.clear_widgets()

        can_edit = role_name in ['admin', 'manager']
        can_view = True
        can_manage_users = role_name == 'admin'

        # Карточка приветствия
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.graphics import Color, RoundedRectangle

        welcome_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=dp(15),
            spacing=dp(10),
        )
        with welcome_card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=welcome_card.pos, size=welcome_card.size, radius=[8])
        welcome_card.add_widget(Label(
            text='Добро пожаловать!',
            font_size='18sp',
            bold=True,
            color=(0.13, 0.13, 0.13, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left',
        ))
        welcome_card.add_widget(Label(
            text='Используйте меню ниже для навигации',
            font_size='13sp',
            color=(0.46, 0.46, 0.46, 1),
            halign='left',
            text_size=(None, None),
        ))
        container.add_widget(welcome_card)

        if can_view:
            container.add_widget(self._make_menu_button(
                'Список деталей', '#1976D2',
                lambda x: setattr(self.manager, 'current', 'details_list')
            ))

        if can_edit:
            container.add_widget(self._make_menu_button(
                'Оформить приход', '#4CAF50',
                lambda x: self._go_to_operation('receive')
            ))
            container.add_widget(self._make_menu_button(
                'Оформить расход', '#F44336',
                lambda x: self._go_to_operation('issue')
            ))

        if can_manage_users:
            container.add_widget(self._make_menu_button(
                'Управление пользователями', '#FF9800',
                lambda x: setattr(self.manager, 'current', 'users')
            ))

    def _make_menu_button(self, text, color_hex, callback):
        from kivy.utils import get_color_from_hex
        btn = Button(
            text=text,
            background_color=get_color_from_hex(color_hex),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(50),
        )
        btn.bind(on_release=callback)
        return btn

    def _go_to_operation(self, operation_type: str):
        self.manager.current = "operation"
        op_screen = self.manager.get_screen("operation")
        op_screen.operation_type = operation_type
        op_screen.ids.operation_title.text = 'Приход' if operation_type == 'receive' else 'Расход'
        op_screen.ids.submit_button.background_color = (0.3, 0.8, 0.3, 1) if operation_type == 'receive' else (0.957, 0.263, 0.212, 1)

    def logout(self) -> None:
        app = App.get_running_app()
        session = getattr(app, "current_session", None)
        if session:
            session.close()
        app.current_user = None
        app.current_session = None
        self.welcome_text = ""
        self.manager.current = "login"


class WarehouseApp(App):
    title = "Учёт деталей на складе"
    current_user = None
    current_session = None

    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(DetailsListScreen(name="details_list"))
        sm.add_widget(DetailFormScreen(name="detail_form"))
        sm.add_widget(DetailViewScreen(name="detail_view"))
        sm.add_widget(UsersScreen(name="users"))
        sm.add_widget(OperationScreen(name="operation"))
        return sm