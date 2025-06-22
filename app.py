"""
Точка входа для Railway
"""
import sys
import os

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем приложение
from backend.main import app

# Экспортируем для uvicorn
__all__ = ['app']