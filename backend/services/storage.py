"""
Сервис для работы с файловым хранилищем
"""
import os
import logging
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime

from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class StorageService:
    """
    Универсальный сервис для работы с файлами
    Поддерживает локальное хранилище и облачные сервисы
    """
    
    def __init__(self):
        self.storage_type = settings.actual_storage_type
        self.base_path = Path(settings.upload_path)
        
        # Создаем директории для локального хранилища
        if self.storage_type == "local":
            self._ensure_directories()
    
    def _ensure_directories(self):
        """Создает необходимые директории"""
        directories = [
            self.base_path / "photos",
            self.base_path / "reports",
            self.base_path / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    async def save_photo(
        self,
        file_data: bytes,
        photo_type: str,
        user_id: int,
        original_filename: Optional[str] = None
    ) -> str:
        """
        Сохраняет фотографию
        
        Args:
            file_data: Данные файла
            photo_type: Тип фотографии
            user_id: ID пользователя
            original_filename: Оригинальное имя файла
            
        Returns:
            Путь к сохраненному файлу
        """
        # Генерируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = ".jpg"
        
        if original_filename:
            _, ext = os.path.splitext(original_filename)
            if ext:
                extension = ext
        
        filename = f"{photo_type}_{user_id}_{timestamp}{extension}"
        
        if self.storage_type == "local":
            # Локальное сохранение
            file_path = self.base_path / "photos" / filename
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Photo saved locally: {file_path}")
            return str(file_path.relative_to(self.base_path))
        
        elif self.storage_type == "cloudinary":
            # Загрузка в Cloudinary
            # TODO: Реализовать загрузку в Cloudinary
            logger.warning("Cloudinary storage not implemented yet")
            return await self._fallback_to_local(file_data, filename)
        
        elif self.storage_type == "s3":
            # Загрузка в S3
            # TODO: Реализовать загрузку в S3
            logger.warning("S3 storage not implemented yet")
            return await self._fallback_to_local(file_data, filename)
        
        else:
            # Неизвестный тип хранилища
            logger.error(f"Unknown storage type: {self.storage_type}")
            return await self._fallback_to_local(file_data, filename)
    
    async def _fallback_to_local(self, file_data: bytes, filename: str) -> str:
        """Резервное сохранение в локальное хранилище"""
        file_path = self.base_path / "photos" / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        logger.info(f"Photo saved locally (fallback): {file_path}")
        return str(file_path.relative_to(self.base_path))
    
    async def get_photo(self, file_path: str) -> Optional[bytes]:
        """
        Получает фотографию по пути
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Данные файла или None
        """
        if self.storage_type == "local":
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                logger.error(f"File not found: {full_path}")
                return None
            
            with open(full_path, 'rb') as f:
                return f.read()
        
        # TODO: Реализовать для облачных хранилищ
        return None
    
    async def delete_photo(self, file_path: str) -> bool:
        """
        Удаляет фотографию
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если успешно удален
        """
        if self.storage_type == "local":
            full_path = self.base_path / file_path
            
            if full_path.exists():
                os.remove(full_path)
                logger.info(f"File deleted: {full_path}")
                return True
            
            logger.warning(f"File not found for deletion: {full_path}")
            return False
        
        # TODO: Реализовать для облачных хранилищ
        return False
    
    async def save_report(
        self,
        file_data: BinaryIO,
        report_type: str,
        format: str = "xlsx"
    ) -> str:
        """
        Сохраняет отчет
        
        Args:
            file_data: Данные файла
            report_type: Тип отчета
            format: Формат файла
            
        Returns:
            Путь к сохраненному файлу
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{timestamp}.{format}"
        
        if self.storage_type == "local":
            file_path = self.base_path / "reports" / filename
            
            # Копируем данные из BytesIO
            file_data.seek(0)
            with open(file_path, 'wb') as f:
                f.write(file_data.read())
            
            logger.info(f"Report saved: {file_path}")
            return str(file_path.relative_to(self.base_path))
        
        # TODO: Реализовать для облачных хранилищ
        return ""
    
    async def cleanup_old_files(self, days: int = 30):
        """
        Удаляет старые файлы
        
        Args:
            days: Файлы старше этого количества дней будут удалены
        """
        if self.storage_type != "local":
            logger.warning("Cleanup not implemented for cloud storage")
            return
        
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        # Проверяем все файлы
        for directory in ["photos", "reports", "temp"]:
            dir_path = self.base_path / directory
            
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    # Проверяем время модификации
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.debug(f"Deleted old file: {file_path}")
        
        logger.info(f"Cleanup completed. Deleted {deleted_count} files older than {days} days")
    
    def get_storage_info(self) -> dict:
        """
        Получает информацию о хранилище
        
        Returns:
            Словарь с информацией
        """
        info = {
            "type": self.storage_type,
            "base_path": str(self.base_path)
        }
        
        if self.storage_type == "local":
            # Подсчитываем файлы и размер
            total_files = 0
            total_size = 0
            
            for directory in ["photos", "reports", "temp"]:
                dir_path = self.base_path / directory
                
                if dir_path.exists():
                    for file_path in dir_path.iterdir():
                        if file_path.is_file():
                            total_files += 1
                            total_size += file_path.stat().st_size
            
            info.update({
                "total_files": total_files,
                "total_size_mb": round(total_size / 1024 / 1024, 2)
            })
        
        return info


# Глобальный экземпляр сервиса
storage_service = StorageService()

# Экспорт
__all__ = ['StorageService', 'storage_service']