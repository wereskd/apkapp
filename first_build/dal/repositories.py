"""Репозитории для работы с базой данных (Data Access Layer)."""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from domain.entities import (
    Base, Category, Detail, OperationType, Role, StockOperation,
    Supplier, Unit, User,
)


class BaseRepository:
    """Базовый репозиторий с общими операциями."""
    model: type[Base]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, pk: int):
        return self.session.get(self.model, pk)

    def list(self):
        return list(self.session.scalars(select(self.model)).all())

    def add(self, obj):
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete(self, obj) -> None:
        self.session.delete(obj)


class UserRepository(BaseRepository):
    model = User

    def get_by_username(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.username == username)
        )

    def list_active(self) -> list[User]:
        return list(self.session.scalars(
            select(User).where(User.is_active.is_(True))
        ).all())

    def get_role_by_name(self, name: str) -> Role | None:
        return self.session.scalar(select(Role).where(Role.name == name))


class DetailRepository(BaseRepository):
    model = Detail

    def get_by_sku(self, sku: str) -> Detail | None:
        return self.session.scalar(select(Detail).where(Detail.sku == sku))

    def search(
        self,
        query: str | None = None,
        category_id: int | None = None,
        only_in_stock: bool = False,
    ) -> list[Detail]:
        stmt = select(Detail)
        if query:
            like = f"%{query}%"
            stmt = stmt.where((Detail.sku.ilike(like)) | (Detail.name.ilike(like)))
        if category_id:
            stmt = stmt.where(Detail.category_id == category_id)
        if only_in_stock:
            stmt = stmt.where(Detail.quantity > 0)
        return list(self.session.scalars(stmt.order_by(Detail.name)).all())

    def list_low_stock(self) -> list[Detail]:
        return list(self.session.scalars(
            select(Detail).where(Detail.quantity <= Detail.min_quantity)
        ).all())


class StockOperationRepository(BaseRepository):
    model = StockOperation

    def list_by_detail(self, detail_id: int) -> list[StockOperation]:
        return list(self.session.scalars(
            select(StockOperation)
            .where(StockOperation.detail_id == detail_id)
            .order_by(StockOperation.operation_date.desc())
        ).all())

    def get_type_by_code(self, code: str) -> OperationType | None:
        return self.session.scalar(
            select(OperationType).where(OperationType.code == code)
        )


class CategoryRepository(BaseRepository):
    model = Category

    def get_by_name(self, name: str) -> Category | None:
        return self.session.scalar(select(Category).where(Category.name == name))


class UnitRepository(BaseRepository):
    model = Unit

    def get_by_short(self, short: str) -> Unit | None:
        return self.session.scalar(select(Unit).where(Unit.short_name == short))


class SupplierRepository(BaseRepository):
    model = Supplier

    def get_by_name(self, name: str) -> Supplier | None:
        return self.session.scalar(select(Supplier).where(Supplier.name == name))