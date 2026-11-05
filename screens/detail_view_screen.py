"""Экран просмотра детали и истории операций."""
from __future__ import annotations

from kivy.app import App
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from business.services import DetailService, OperationService
from database.connection import get_session


def format_quantity(value) -> str:
    try:
        return f"{float(value):g}"
    except (ValueError, TypeError):
        return str(value)


def show_popup(title: str, message: str) -> None:
    popup = Popup(
        title=title,
        content=Label(text=message, font_size='16sp'),
        size_hint=(0.9, 0.3),
        auto_dismiss=True,
    )
    popup.open()


def show_confirm_popup(title: str, message: str, on_confirm) -> None:
    """Показывает окно подтверждения действия."""
    content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
    content.add_widget(Label(text=message, font_size='16sp', halign='center'))

    buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

    # Создаем popup ДО кнопок, чтобы он был доступен в замыканиях
    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.9, 0.35),
        auto_dismiss=False,
    )

    btn_confirm = Button(
        text='Да',
        background_color=(0.957, 0.263, 0.212, 1),
        color=(1, 1, 1, 1),
        font_size='14sp',
        bold=True,
    )
    btn_confirm.bind(on_release=lambda x: (popup.dismiss(), on_confirm()))

    btn_cancel = Button(
        text='Отмена',
        background_color=(0.96, 0.96, 0.96, 1),
        color=(0.098, 0.463, 0.824, 1),
        font_size='14sp',
    )
    btn_cancel.bind(on_release=lambda x: popup.dismiss())

    buttons.add_widget(btn_confirm)
    buttons.add_widget(btn_cancel)
    content.add_widget(buttons)

    popup.open()


class DetailViewScreen(Screen):
    detail_id = NumericProperty(None)

    def on_enter(self) -> None:
        if self.detail_id:
            self.clear_widgets()
            self._build_ui()
            self.load_detail()
            self.load_operations()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical')

        with self.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        header = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(15), 0],
        )
        with header.canvas.before:
            Color(0.098, 0.463, 0.824, 1)
            RoundedRectangle(pos=header.pos, size=header.size, radius=[0])
        header.bind(
            size=self._update_header_bg,
            pos=self._update_header_bg,
        )

        self.title_label = Label(
            text='Деталь',
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left',
        )
        header.add_widget(self.title_label)

        back_btn = Button(
            text='Назад',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.082, 0.396, 0.753, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        header.add_widget(back_btn)
        root.add_widget(header)

        scroll = ScrollView()
        self.content_box = BoxLayout(
            orientation='vertical',
            padding=[dp(15), dp(10)],
            spacing=dp(10),
            size_hint_y=None,
        )
        self.content_box.bind(minimum_height=self.content_box.setter('height'))
        scroll.add_widget(self.content_box)
        root.add_widget(scroll)

        self.add_widget(root)

    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _update_header_bg(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.098, 0.463, 0.824, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[0])

    def _make_header(self, text: str):
        return Label(
            text=text,
            font_size='15sp',
            bold=True,
            color=(0.098, 0.463, 0.824, 1),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            markup=False,
        )

    def _make_info_row(self, label_text: str, value: str):
        row = BoxLayout(
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10),
        )
        row.add_widget(Label(
            text=label_text,
            size_hint_x=None,
            width=dp(120),
            halign='left',
            font_size='13sp',
            color=(0.46, 0.46, 0.46, 1),
        ))
        row.add_widget(Label(
            text=value,
            halign='left',
            font_size='13sp',
            bold=True,
            color=(0.13, 0.13, 0.13, 1),
        ))
        return row

    def load_detail(self) -> None:
        session = get_session()
        try:
            service = DetailService(session)
            detail = service.details.get(self.detail_id)

            if not detail:
                self.content_box.add_widget(Label(
                    text="Деталь не найдена",
                    size_hint_y=None,
                    height=dp(40),
                    font_size='14sp',
                    color=(0.5, 0.5, 0.5, 1),
                ))
                return

            self.title_label.text = f"{detail.sku} - {detail.name}"

            self.content_box.add_widget(self._make_header('Информация о детали'))

            info_fields = [
                ("Артикул:", detail.sku),
                ("Название:", detail.name),
                ("Категория:", detail.category.name),
                ("Ед. изм.:", f"{detail.unit.short_name} ({detail.unit.full_name})"),
                ("Остаток:", f"{format_quantity(detail.quantity)} {detail.unit.short_name}"),
                ("Мин. остаток:", f"{format_quantity(detail.min_quantity)} {detail.unit.short_name}"),
            ]
            if detail.comment:
                info_fields.append(("Комментарий:", detail.comment))

            for label_text, value in info_fields:
                self.content_box.add_widget(self._make_info_row(label_text, value))

            self.content_box.add_widget(self._make_header('История операций'))
            self.ops_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                spacing=dp(6),
            )
            self.ops_container.bind(minimum_height=self.ops_container.setter('height'))
            self.content_box.add_widget(self.ops_container)

            # Кнопки только для admin и manager
            user = getattr(App.get_running_app(), "current_user", None)
            can_edit = user and user.role.name in ['admin', 'manager']

            if can_edit:
                btn_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))

                edit_btn = Button(
                    text='Редактировать',
                    background_color=(0.3, 0.7, 0.9, 1),
                    color=(1, 1, 1, 1),
                    font_size='14sp',
                    bold=True,
                )
                edit_btn.bind(on_release=lambda x: self.go_to_edit())
                btn_row.add_widget(edit_btn)

                del_btn = Button(
                    text='Удалить',
                    background_color=(0.9, 0.5, 0.5, 1),
                    color=(1, 1, 1, 1),
                    font_size='14sp',
                    bold=True,
                )
                del_btn.bind(on_release=lambda x: self.delete_detail())
                btn_row.add_widget(del_btn)

                self.content_box.add_widget(btn_row)

        except Exception as e:
            show_popup("Ошибка", str(e))
        finally:
            session.close()
    def load_operations(self) -> None:
        session = get_session()
        try:
            service = OperationService(session)
            operations = service.history(self.detail_id)

            if not operations:
                self.ops_container.add_widget(Label(
                    text="Операции не найдены",
                    size_hint_y=None,
                    height=dp(40),
                    font_size='14sp',
                    color=(0.3, 0.3, 0.3, 1),  # Тёмно-серый для читаемости
                ))
                return

            for op in operations:
                type_name = op.type.name if op.type else "Неизвестно"
                user_name = op.user.full_name if op.user else "Неизвестно"
                supplier_name = op.supplier.name if op.supplier else "-"
                date_str = op.operation_date.strftime('%Y-%m-%d %H:%M') if op.operation_date else "-"

                text = (
                    f"{type_name}  {format_quantity(op.quantity)}  {date_str}\n"
                    f"Пользователь: {user_name}  |  Поставщик: {supplier_name}"
                )
                if op.comment:
                    text += f"\nКомментарий: {op.comment}"

                btn = Button(
                    text=text,
                    background_color=(1, 1, 1, 1),  # Чисто белый фон вместо серого
                    color=(0, 0, 0, 1),             # Чисто чёрный текст
                    font_size='12sp',
                    halign='left',
                    valign='middle',
                    size_hint_y=None,
                    height=dp(60),
                    padding=[dp(10), dp(8)],
                )
                
                with btn.canvas.before:
                    from kivy.graphics import Color, RoundedRectangle
                    Color(1, 1, 1, 1)
                    RoundedRectangle(pos=btn.pos, size=btn.size, radius=[6])
                    
                self.ops_container.add_widget(btn)

        except Exception as e:
            show_popup("Ошибка", str(e))
        finally:
            session.close()

    def go_to_edit(self) -> None:
        self.manager.current = "detail_form"
        form_screen = self.manager.get_screen("detail_form")
        form_screen.is_edit_mode = True
        form_screen.detail_id = self.detail_id

    def delete_detail(self) -> None:
        def on_confirm():
            session = get_session()
            try:
                service = DetailService(session)
                service.delete(self.detail_id)
                session.commit()
                show_popup("Успех", "Деталь удалена!")
                self.go_back()
            except ValueError as e:
                show_popup("Ошибка", str(e))
                session.rollback()
            except Exception as e:
                show_popup("Ошибка", str(e))
                session.rollback()
            finally:
                session.close()

        show_confirm_popup(
            "Подтверждение",
            "Вы уверены, что хотите удалить эту деталь?",
            on_confirm,
        )

    def go_back(self) -> None:
        self.manager.current = "details_list"