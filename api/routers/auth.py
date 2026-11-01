"""Роутеры для авторизации и регистрации."""
from __future__ import annotations
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_db,
)
from api.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from business.services import AuthService, hash_password
from domain.entities import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Вход в систему.
    Возвращает JWT токен для дальнейших запросов.
    """
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Обновляем last_login
    user.last_login = datetime.utcnow()
    db.flush()

    # Создаём токен
    access_token = create_access_token(data={"sub": user.username})

    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.
    Пароль автоматически хешируется.
    """
    service = AuthService(db)
    try:
        user = service.register(
            username=request.username,
            password=request.password,
            full_name=request.full_name,
            role_name=request.role_name,
        )
        db.commit()
        db.refresh(user)
        return UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role_name=user.role.name,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущем пользователе.
    Защищённый endpoint — требует валидный JWT токен.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role_name=current_user.role.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )