"""Сущности предметной области (Модели БД)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    details: Mapped[list["Detail"]] = relationship(back_populates="category")


class Unit(Base):
    __tablename__ = "units"
    id: Mapped[int] = mapped_column(primary_key=True)
    short_name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[list["Detail"]] = relationship(back_populates="unit")


class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact: Mapped[str | None] = mapped_column(String(200))
    operations: Mapped[list["StockOperation"]] = relationship(back_populates="supplier")


class OperationType(Base):
    __tablename__ = "operation_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    operations: Mapped[list["StockOperation"]] = relationship(back_populates="type")


class User(Base):
    __tablename__ = "app_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column("password_hash", String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    role: Mapped["Role"] = relationship(back_populates="users")
    operations: Mapped[list["StockOperation"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Detail(Base):
    __tablename__ = "details"
    __table_args__ = (CheckConstraint("min_quantity >= 0", name="ck_detail_min_qty"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable=False)
    min_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    category: Mapped["Category"] = relationship(back_populates="details")
    unit: Mapped["Unit"] = relationship(back_populates="details")
    operations: Mapped[list["StockOperation"]] = relationship(back_populates="detail")

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.min_quantity

    def __repr__(self) -> str:
        return f"<Detail {self.sku} {self.name}>"


class StockOperation(Base):
    __tablename__ = "stock_operations"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_op_qty_positive"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    detail_id: Mapped[int] = mapped_column(ForeignKey("details.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.id"), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("operation_types.id"), nullable=False)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    operation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    responsible: Mapped[str | None] = mapped_column(String(150))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Поле status с значением по умолчанию из БД (исправлено для SQLAlchemy 2.0)
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        server_default=text("'CREATED'")
    )

    detail: Mapped["Detail"] = relationship(back_populates="operations")
    user: Mapped["User"] = relationship(back_populates="operations")
    type: Mapped["OperationType"] = relationship(back_populates="operations")
    supplier: Mapped["Supplier | None"] = relationship(back_populates="operations")