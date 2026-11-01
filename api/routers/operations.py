"""Роутеры для операций прихода и расхода."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user, get_db
from api.schemas import OperationCreate, OperationResponse
from business.services import OperationService
from domain.entities import User

router = APIRouter(prefix="/api/operations", tags=["operations"])


@router.get("", response_model=list[OperationResponse])
def list_operations(
    limit: int = Query(50, ge=1, le=200, description="Максимум записей"),
    detail_id: int | None = Query(None, description="Фильтр по ID детали"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получение списка операций.
    Можно фильтровать по detail_id.
    """
    service = OperationService(db)
    
    if detail_id:
        operations = service.history(detail_id)
    else:
        # Получаем последние операции через репозиторий
        from dal.repositories import StockOperationRepository
        repo = StockOperationRepository(db)
        operations = repo.list()[:limit]
    
    # Преобразуем в формат ответа
    result = []
    for op in operations:
        result.append(OperationResponse(
            id=op.id,
            detail_id=op.detail_id,
            user_id=op.user_id,
            type_code=op.type.code if op.type else "UNKNOWN",
            quantity=op.quantity,
            operation_date=op.operation_date,
            supplier_name=op.supplier.name if op.supplier else None,
            responsible=op.responsible,
            comment=op.comment,
            status=op.status,
        ))
    
    return result


@router.post("/receive", response_model=OperationResponse, status_code=status.HTTP_201_CREATED)
def receive_operation(
    request: OperationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Операция прихода (увеличение остатка).
    """
    service = OperationService(db)
    try:
        operation = service.receive(
            detail_id=request.detail_id,
            user=current_user,
            quantity=request.quantity,
            supplier_name=request.supplier_name,
            comment=request.comment,
        )
        db.commit()
        db.refresh(operation)
        
        return OperationResponse(
            id=operation.id,
            detail_id=operation.detail_id,
            user_id=operation.user_id,
            type_code=operation.type.code if operation.type else "IN",
            quantity=operation.quantity,
            operation_date=operation.operation_date,
            supplier_name=operation.supplier.name if operation.supplier else None,
            responsible=operation.responsible,
            comment=operation.comment,
            status=operation.status,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/issue", response_model=OperationResponse, status_code=status.HTTP_201_CREATED)
def issue_operation(
    request: OperationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Операция расхода (уменьшение остатка).
    """
    service = OperationService(db)
    try:
        operation = service.issue(
            detail_id=request.detail_id,
            user=current_user,
            quantity=request.quantity,
            responsible=request.responsible,
            comment=request.comment,
        )
        db.commit()
        db.refresh(operation)
        
        return OperationResponse(
            id=operation.id,
            detail_id=operation.detail_id,
            user_id=operation.user_id,
            type_code=operation.type.code if operation.type else "OUT",
            quantity=operation.quantity,
            operation_date=operation.operation_date,
            supplier_name=operation.supplier.name if operation.supplier else None,
            responsible=operation.responsible,
            comment=operation.comment,
            status=operation.status,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{operation_id}", response_model=OperationResponse)
def get_operation(
    operation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получение информации о конкретной операции.
    """
    from dal.repositories import StockOperationRepository
    repo = StockOperationRepository(db)
    operation = repo.get(operation_id)
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Операция не найдена",
        )
    
    return OperationResponse(
        id=operation.id,
        detail_id=operation.detail_id,
        user_id=operation.user_id,
        type_code=operation.type.code if operation.type else "UNKNOWN",
        quantity=operation.quantity,
        operation_date=operation.operation_date,
        supplier_name=operation.supplier.name if operation.supplier else None,
        responsible=operation.responsible,
        comment=operation.comment,
        status=operation.status,
    )


@router.get("/detail/{detail_id}", response_model=list[OperationResponse])
def get_operations_by_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получение истории операций по конкретной детали.
    """
    service = OperationService(db)
    operations = service.history(detail_id)
    
    result = []
    for op in operations:
        result.append(OperationResponse(
            id=op.id,
            detail_id=op.detail_id,
            user_id=op.user_id,
            type_code=op.type.code if op.type else "UNKNOWN",
            quantity=op.quantity,
            operation_date=op.operation_date,
            supplier_name=op.supplier.name if op.supplier else None,
            responsible=op.responsible,
            comment=op.comment,
            status=op.status,
        ))
    
    return result