# backend_main.py
"""Точка входа для серверной части (Бэкенд)."""
import uvicorn
from api.app import app  # Импортируй твое FastAPI/Flask приложение

if __name__ == "__main__":
    print("Запуск Backend сервера...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True  # В продакшене лучше поставить False
    )