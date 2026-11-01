"""Pydantic-схемы для API (DTO)."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional


# ============================================================================
# Схемы для авторизации
# ============================================================================
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    role_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role_name: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Схемы для деталей
# ============================================================================
class DetailCreate(BaseModel):
    sku: str
    name: str
    category_name: str
    unit_short: str
    min_quantity: Decimal = Decimal("0")


class DetailUpdate(BaseModel):
    name: Optional[str] = None
    min_quantity: Optional[Decimal] = None
    comment: Optional[str] = None


class UnitResponse(BaseModel):
    id: int
    short_name: str
    full_name: str

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class DetailResponse(BaseModel):
    id: int
    sku: str
    name: str
    category: CategoryResponse
    unit: UnitResponse
    min_quantity: Decimal
    quantity: Decimal
    comment: Optional[str] = None
    created_at: datetime
    is_low_stock: bool

    class Config:
        from_attributes = True


class PaginatedDetailsResponse(BaseModel):
    """Ответ с пагинацией (требование 3.f)."""
    items: list[DetailResponse]
    total: int
    page: int
    limit: int
    pages: int


# ============================================================================
# Схемы для операций
# ============================================================================
class OperationCreate(BaseModel):
    detail_id: int
    quantity: Decimal = Field(gt=0)
    supplier_name: Optional[str] = None
    responsible: Optional[str] = None
    comment: Optional[str] = None


class OperationResponse(BaseModel):
    id: int
    detail_id: int
    user_id: int
    type_code: str
    quantity: Decimal
    operation_date: datetime
    supplier_name: Optional[str] = None
    responsible: Optional[str] = None
    comment: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True