"""Экран оформления операций прихода и расхода."""
from __future__ import annotations

from decimal import Decimal
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from business.services import OperationService
from dal.repositories import DetailRepository
from database.connection import get_session

KV = """
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<OperationScreen>:
    name: 'operation'
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
                id: operation_title
                text: 'Операция'
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
                    text: 'Деталь'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                Spinner:
                    id: detail_spinner
                    text: 'Выберите деталь'
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    color: 0, 0, 0, 1

                Label:
                    text: 'Количество'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: quantity_input
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
                    text: 'Поставщик / Ответственный'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: person_input
                    hint_text: 'Имя'
                    multiline: False
                    size_hint_y: None
                    height: dp(40)
                    font_size: '14sp'
                    background_color: get_color_from_hex('#FFFFFF')
                    foreground_color: 0, 0, 0, 1
                    cursor_color: 0.098, 0.463, 0.824, 1
                    hint_text_color: 0.5, 0.5, 0.5, 1

                Label:
                    text: 'Комментарий'
                    font_size: '13sp'
                    color: get_color_from_hex('#757575')
                    size_hint_y: None
                    height: dp(20)
                    halign: 'left'

                TextInput:
                    id: comment_input
                    hint_text: 'Комментарий'
                    multiline: True
                    size_hint_y: None
                    height: dp(80)
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
                    id: submit_button
                    text: 'Оформить'
                    background_color: get_color_from_hex('#4CAF50')
                    color: get_color_from_hex('#FFFFFF')
                    font_size: '15sp'
                    bold: True
                    size_hint_y: None
                    height: dp(45)
                    on_release: root.submit_operation()
"""

Builder.load_string(KV)


def show_popup(title: str, message: str) -> None:
    """Показывает всплывающее окно."""
    popup = Popup(
        title=title,
        content=Label(text=message, font_size='16sp'),
        size_hint=(0.9, 0.3),
        auto_dismiss=True,
    )
    popup.open()


class OperationScreen(Screen):
    """Экран оформления операций прихода/расхода."""

    operation_type = None  # 'receive' или 'issue'
    detail_ids = []  # Список ID деталей параллельно значениям Spinner

    def on_enter(self) -> None:
        """Проверяем права и загружаем список деталей."""
        user = getattr(App.get_running_app(), "current_user", None)
        if not user or user.role.name not in ['admin', 'manager']:
            show_popup("Ошибка", "Доступ запрещён")
            self.manager.current = "main"
            return
        self.load_details()

    def load_details(self) -> None:
        """Загружает список деталей в Spinner."""
        self.detail_ids = []
        session = get_session()
        try:
            repo = DetailRepository(session)
            details = repo.list()

            if details:
                # Формат: "sku - name (Остаток: qty unit)"
                detail_texts = [
                    f"{d.sku} - {d.name} (Остаток: {float(d.quantity):g} {d.unit.short_name})"
                    for d in details
                ]
                # Сохраняем ID параллельно
                self.detail_ids = [d.id for d in details]

                self.ids.detail_spinner.values = detail_texts
                self.ids.detail_spinner.text = detail_texts[0]
        except Exception as e:
            show_popup("Ошибка", str(e))
        finally:
            session.close()

    def submit_operation(self) -> None:
        """Оформляет операцию прихода или расхода."""
        detail_text = self.ids.detail_spinner.text
        quantity_str = self.ids.quantity_input.text.strip()
        person = self.ids.person_input.text.strip()
        comment = self.ids.comment_input.text.strip()
        error = self.ids.error_label

        if not detail_text or not quantity_str:
            error.text = "Выберите деталь и укажите количество"
            return

        try:
            quantity = Decimal(quantity_str)
        except Exception:
            error.text = "Неверный формат количества"
            return

        # Получаем ID детали по индексу выбранного текста
        try:
            selected_index = self.ids.detail_spinner.values.index(detail_text)
            detail_id = self.detail_ids[selected_index]
        except (ValueError, IndexError):
            error.text = "Ошибка выбора детали"
            return

        session = get_session()
        try:
            service = OperationService(session)
            user = App.get_running_app().current_user

            if self.operation_type == 'receive':
                service.receive(
                    detail_id=detail_id,
                    user=user,
                    quantity=quantity,
                    supplier_name=person if person else None,
                    comment=comment if comment else None,
                )
            else:  # issue
                service.issue(
                    detail_id=detail_id,
                    user=user,
                    quantity=quantity,
                    responsible=person if person else None,
                    comment=comment if comment else None,
                )

            session.commit()
            error.text = ""
            show_popup(
                "Успех",
                f"Операция {'прихода' if self.operation_type == 'receive' else 'расхода'} оформлена!"
            )
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
        """Возврат на главный экран."""
        self.manager.current = "main"