"""Бизнес-логика приложения."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from domain.entities import Category, Detail, StockOperation, Supplier, Unit, User
from dal.repositories import (
    CategoryRepository,
    DetailRepository,
    StockOperationRepository,
    SupplierRepository,
    UnitRepository,
    UserRepository,
)
import bcrypt


def hash_password(password: str) -> str:
    """Хеширует пароль через bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль через bcrypt."""
    pwd_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


class AuthService:
    """Сервис авторизации и регистрации пользователей."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def login(self, username: str, password: str) -> User:
        """Вход в систему."""
        user = self.users.get_by_username(username)
        if not user or not user.is_active:
            raise ValueError("Пользователь не найден или заблокирован")

        if not verify_password(password, user.password_hash):
            raise ValueError("Неверный пароль")

        user.last_login = datetime.utcnow()
        self.session.flush()

        return user

    def register(
        self,
        username: str,
        password: str,
        full_name: str,
        role_name: str,
        current_user: User | None = None,
    ) -> User:
        """
        Регистрация нового пользователя.
        Только admin может создавать других admin.
        Доступные роли согласно ТЗ: admin, manager, observer.
        """
        # Проверка на создание админа
        if role_name == "admin" and (
            not current_user or current_user.role.name != "admin"
        ):
            raise ValueError(
                "Создать администратора может только существующий администратор"
            )

        # Проверка допустимых ролей согласно Vision/SAD
        valid_roles = ["admin", "manager", "observer"]
        if role_name not in valid_roles:
            raise ValueError(f"Недопустимая роль '{role_name}'")

        if self.users.get_by_username(username):
            raise ValueError(f"Пользователь '{username}' уже существует")

        role = self.users.get_role_by_name(role_name)
        if not role:
            raise ValueError(f"Роль '{role_name}' не найдена в БД")

        hashed_pw = hash_password(password)

        user = User(
            username=username,
            password_hash=hashed_pw,
            full_name=full_name,
            role_id=role.id,
        )
        self.users.add(user)
        return user


class DetailService:
    """Сервис управления деталями."""

    def __init__(self, session: Session, user: User | None = None) -> None:
        self.session = session
        self.user = user
        self.details = DetailRepository(session)
        self.categories = CategoryRepository(session)
        self.units = UnitRepository(session)

    def _check_edit_permission(self) -> None:
        """Проверяет права на редактирование (USC-03, 04, 05)."""
        allowed_roles = ["admin", "manager"]
        if not self.user or self.user.role.name not in allowed_roles:
            raise ValueError("У вас нет прав для изменения деталей")

    def create(
        self,
        sku: str,
        name: str,
        category_name: str,
        unit_short: str,
        min_quantity: Decimal = Decimal("0"),
    ) -> Detail:
        """Создание новой детали с авто-созданием справочников."""
        self._check_edit_permission()

        if self.details.get_by_sku(sku):
            raise ValueError(f"Деталь с артикулом '{sku}' уже существует")

        # Категория: создаём, если не найдена
        category = self.categories.get_by_name(category_name)
        if not category:
            category = self.categories.add(Category(name=category_name))

        # Единица измерения: создаём, если не найдена
        unit = self.units.get_by_short(unit_short)
        if not unit:
            unit = self.units.add(Unit(
                short_name=unit_short,
                full_name=unit_short,
            ))

        detail = Detail(
            sku=sku,
            name=name,
            category_id=category.id,
            unit_id=unit.id,
            min_quantity=min_quantity,
            quantity=Decimal("0"),
        )
        return self.details.add(detail)

    def update(self, detail_id: int, **fields) -> Detail:
        """Обновление существующей детали."""
        self._check_edit_permission()

        detail = self.details.get(detail_id)
        if not detail:
            raise ValueError("Деталь не найдена")

        for key, value in fields.items():
            if value is not None and hasattr(detail, key):
                setattr(detail, key, value)

        self.session.flush()
        return detail

    def delete(self, detail_id: int) -> None:
        """Удаление детали (только если остаток равен 0)."""
        self._check_edit_permission()

        detail = self.details.get(detail_id)
        if not detail:
            raise ValueError("Деталь не найдена")

        if detail.quantity != 0:
            raise ValueError(
                f"Нельзя удалить деталь с остатком {detail.quantity}. "
                f"Сначала обнулите остаток."
            )

        self.details.delete(detail)

    def search(self, query=None, category_id=None, only_in_stock=False):
        """Поиск деталей с фильтрацией (USC-08)."""
        return self.details.search(query, category_id, only_in_stock)

    def low_stock(self):
        """Получение списка деталей с низким остатком."""
        return self.details.list_low_stock()


class OperationService:
    """Сервис оформления операций прихода и расхода."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.details = DetailRepository(session)
        self.operations = StockOperationRepository(session)
        self.suppliers = SupplierRepository(session)

    def receive(
        self,
        detail_id: int,
        user: User,
        quantity: Decimal,
        supplier_name: str | None = None,
        comment: str | None = None,
    ) -> StockOperation:
        """Оформление операции прихода (USC-06)."""
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        detail = self.details.get(detail_id)
        if not detail:
            raise ValueError("Деталь не найдена")

        type_in = self.operations.get_type_by_code("IN")
        if not type_in:
            raise ValueError("Тип операции 'IN' не найден")

        supplier = None
        if supplier_name:
            supplier = self.suppliers.get_by_name(supplier_name)
            if not supplier:
                supplier = self.suppliers.add(Supplier(name=supplier_name))

        operation = StockOperation(
            detail_id=detail.id,
            user_id=user.id,
            type_id=type_in.id,
            supplier_id=supplier.id if supplier else None,
            quantity=quantity,
            comment=comment,
        )
        self.operations.add(operation)

        detail.quantity = Decimal(detail.quantity) + quantity
        self.session.flush()

        return operation

    def issue(
        self,
        detail_id: int,
        user: User,
        quantity: Decimal,
        responsible: str | None = None,
        comment: str | None = None,
    ) -> StockOperation:
        """Оформление операции расхода (USC-07)."""
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        detail = self.details.get(detail_id)
        if not detail:
            raise ValueError("Деталь не найдена")

        if detail.quantity < quantity:
            raise ValueError(
                f"Недостаточно остатка: есть {detail.quantity}, "
                f"запрошено {quantity}"
            )

        type_out = self.operations.get_type_by_code("OUT")
        if not type_out:
            raise ValueError("Тип операции 'OUT' не найден")

        operation = StockOperation(
            detail_id=detail.id,
            user_id=user.id,
            type_id=type_out.id,
            quantity=quantity,
            responsible=responsible,
            comment=comment,
        )
        self.operations.add(operation)

        detail.quantity = Decimal(detail.quantity) - quantity
        self.session.flush()

        return operation

    def history(self, detail_id: int) -> list[StockOperation]:
        """Получение истории операций по конкретной детали (USC-09)."""
        return self.operations.list_by_detail(detail_id)