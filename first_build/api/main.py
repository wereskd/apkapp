"""Точка входа FastAPI приложения."""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, details, operations

# Создаём приложение
app = FastAPI(
    title="Warehouse Management System API",
    description="API для системы учёта деталей на складе",
    version="1.0.0",
)

# Настраиваем CORS (чтобы GUI мог обращаться к API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажи конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем роутеры
app.include_router(auth.router)
app.include_router(details.router)
app.include_router(operations.router)


@app.get("/")
def root():
    """Корневой endpoint."""
    return {
        "message": "Warehouse Management System API",
        "docs": "/docs",
        "health": "OK",
    }


@app.get("/health")
def health_check():
    """Проверка работоспособности API."""
    return {"status": "healthy"}