"""Зависимости FastAPI: сессия БД и JWT аутентификация."""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from domain.entities import User
from dal.repositories import UserRepository
from business.services import verify_password

# --- Конфигурация JWT ---
SECRET_KEY = "super-secret-key-for-jwt-12345"  # В реальном проекте брать из .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# --- Зависимость для БД (Требование 3.e) ---
def get_db() -> Generator:
    """Получает сессию БД и закрывает её после использования."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Хелперы для JWT ---
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создаёт JWT токен."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Проверяет логин и пароль."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# --- Зависимость для получения текущего пользователя ---
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Декодирует токен и возвращает текущего пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user
def require_role(*roles: str):
    """
    Зависимость для проверки роли пользователя.
    Использование: current_user: User = Depends(require_role("admin", "manager"))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Доступ запрещён. Требуется роль: {', '.join(roles)}",
            )
        return current_user
    return role_checker