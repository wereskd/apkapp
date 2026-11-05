"""Роутеры для CRUD операций с деталями."""
from __future__ import annotations
import math
from decimal import Decimal

from api.dependencies import get_current_user, get_db, require_role
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user, get_db
from api.schemas import (
    DetailCreate,
    DetailResponse,
    DetailUpdate,
    PaginatedDetailsResponse,
)
from business.services import DetailService
from domain.entities import User

router = APIRouter(prefix="/api/details", tags=["details"])


@router.get("", response_model=PaginatedDetailsResponse)
def list_details(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    query: str | None = Query(None, description="Поиск по артикулу или названию"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получение списка деталей с пагинацией (требование 3.f).
    Поддерживает поиск по артикулу/названию.
    """
    service = DetailService(db)
    
    # Получаем все детали с фильтром
    all_items = service.search(query=query)
    total = len(all_items)
    pages = math.ceil(total / limit) if total > 0 else 1
    
    # Применяем пагинацию
    start = (page - 1) * limit
    end = start + limit
    paginated_items = all_items[start:end]
    
    return PaginatedDetailsResponse(
        items=paginated_items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.post("", response_model=DetailResponse, status_code=status.HTTP_201_CREATED)
def create_detail(
    request: DetailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создание новой детали.
    """
    service = DetailService(db)
    try:
        detail = service.create(
            sku=request.sku,
            name=request.name,
            category_name=request.category_name,
            unit_short=request.unit_short,
            min_quantity=request.min_quantity,
        )
        db.commit()
        db.refresh(detail)
        return detail
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{detail_id}", response_model=DetailResponse)
def get_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получение информации о конкретной детали.
    """
    service = DetailService(db)
    detail = service.details.get(detail_id)
    
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Деталь не найдена",
        )
    
    return detail


@router.put("/{detail_id}", response_model=DetailResponse)
def update_detail(
    detail_id: int,
    request: DetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновление существующей детали.
    """
    service = DetailService(db)
    try:
        # Фильтруем только заполненные поля
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        
        detail = service.update(detail_id, **update_data)
        db.commit()
        db.refresh(detail)
        return detail
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{detail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """
    Удаление детали.
    """
    service = DetailService(db)
    try:
        service.delete(detail_id)
        db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )