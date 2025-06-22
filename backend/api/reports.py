"""
API endpoints для отчетов и экспорта данных
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.core.database import get_async_session
from backend.services.reports import ReportService
from backend.models import User, Operation, OperationType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/users/excel")
async def export_users_excel(
    session: AsyncSession = Depends(get_async_session),
    active_only: bool = Query(False, description="Только активные пользователи"),
    role: Optional[str] = Query(None, description="Фильтр по роли")
):
    """
    Экспорт пользователей в Excel
    """
    try:
        report_service = ReportService(session)
        
        # Получаем файл
        excel_file = await report_service.generate_users_report(
            active_only=active_only,
            role_filter=role
        )
        
        # Имя файла
        filename = f"users_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"Failed to generate users report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations/excel")
async def export_operations_excel(
    session: AsyncSession = Depends(get_async_session),
    days: int = Query(7, description="Количество дней", ge=1, le=365),
    user_id: Optional[int] = Query(None, description="ID пользователя"),
    operation_type: Optional[str] = Query(None, description="Тип операции")
):
    """
    Экспорт операций в Excel
    """
    try:
        report_service = ReportService(session)
        
        # Период
        date_from = datetime.now() - timedelta(days=days)
        
        # Получаем файл
        excel_file = await report_service.generate_operations_report(
            date_from=date_from,
            date_to=datetime.now(),
            user_id=user_id,
            operation_type=operation_type
        )
        
        # Имя файла
        filename = f"operations_{days}days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"Failed to generate operations report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/warehouse/stock")
async def get_warehouse_stock_report(
    session: AsyncSession = Depends(get_async_session),
    format: str = Query("json", description="Формат ответа: json или excel")
):
    """
    Отчет по остаткам на складе
    """
    try:
        report_service = ReportService(session)
        
        if format == "excel":
            # Excel файл
            excel_file = await report_service.generate_stock_report()
            filename = f"stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            return StreamingResponse(
                excel_file,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        else:
            # JSON данные
            stock_data = await report_service.get_stock_summary()
            return stock_data
    
    except Exception as e:
        logger.error(f"Failed to generate stock report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/daily")
async def get_daily_summary(
    session: AsyncSession = Depends(get_async_session),
    date: Optional[datetime] = Query(None, description="Дата (по умолчанию - сегодня)")
):
    """
    Дневная сводка по всем операциям
    """
    try:
        if not date:
            date = datetime.now()
        
        # Начало и конец дня
        day_start = date.replace(hour=0, minute=0, second=0)
        day_end = date.replace(hour=23, minute=59, second=59)
        
        # Операции за день
        operations_stmt = select(
            Operation.operation_type,
            func.count(Operation.id).label("count")
        ).where(
            and_(
                Operation.created_at >= day_start,
                Operation.created_at <= day_end
            )
        ).group_by(Operation.operation_type)
        
        result = await session.execute(operations_stmt)
        operations_by_type = {
            op_type: count 
            for op_type, count in result.fetchall()
        }
        
        # Активные пользователи
        active_users_stmt = select(
            func.count(func.distinct(Operation.user_id))
        ).where(
            and_(
                Operation.created_at >= day_start,
                Operation.created_at <= day_end
            )
        )
        
        active_users = await session.scalar(active_users_stmt)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "summary": {
                "total_operations": sum(operations_by_type.values()),
                "active_users": active_users,
                "operations_by_type": operations_by_type
            },
            "details": {
                "warehouse": {
                    "received": operations_by_type.get(OperationType.INVENTORY_RECEIVE, 0),
                    "issued": operations_by_type.get(OperationType.ISSUE_HOPPER, 0),
                    "filled": operations_by_type.get(OperationType.HOPPER_FILL, 0)
                },
                "operator": {
                    "installed": operations_by_type.get(OperationType.HOPPER_INSTALL, 0),
                    "removed": operations_by_type.get(OperationType.HOPPER_REMOVE, 0),
                    "serviced": operations_by_type.get(OperationType.MACHINE_SERVICE, 0)
                },
                "driver": {
                    "trips_started": operations_by_type.get(OperationType.START_TRIP, 0),
                    "trips_ended": operations_by_type.get(OperationType.END_TRIP, 0),
                    "fuel_purchases": operations_by_type.get(OperationType.FUEL_PURCHASE, 0)
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to generate daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/operator/{user_id}")
async def get_operator_performance(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    days: int = Query(30, description="Период в днях", ge=1, le=365)
):
    """
    Отчет по эффективности оператора
    """
    try:
        # Проверяем существование пользователя
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Период
        date_from = datetime.now() - timedelta(days=days)
        
        # Операции оператора
        operations_stmt = select(
            Operation.operation_type,
            func.count(Operation.id).label("count"),
            func.date(Operation.created_at).label("date")
        ).where(
            and_(
                Operation.user_id == user_id,
                Operation.created_at >= date_from,
                Operation.operation_type.in_([
                    OperationType.HOPPER_INSTALL,
                    OperationType.HOPPER_REMOVE,
                    OperationType.MACHINE_SERVICE,
                    OperationType.PROBLEM_REPORT
                ])
            )
        ).group_by(
            Operation.operation_type,
            func.date(Operation.created_at)
        )
        
        result = await session.execute(operations_stmt)
        operations_data = result.fetchall()
        
        # Группируем по дням
        daily_stats = {}
        for op_type, count, date in operations_data:
            date_str = date.strftime("%Y-%m-%d")
            if date_str not in daily_stats:
                daily_stats[date_str] = {
                    "installs": 0,
                    "removes": 0,
                    "services": 0,
                    "problems": 0
                }
            
            if op_type == OperationType.HOPPER_INSTALL:
                daily_stats[date_str]["installs"] = count
            elif op_type == OperationType.HOPPER_REMOVE:
                daily_stats[date_str]["removes"] = count
            elif op_type == OperationType.MACHINE_SERVICE:
                daily_stats[date_str]["services"] = count
            elif op_type == OperationType.PROBLEM_REPORT:
                daily_stats[date_str]["problems"] = count
        
        # Общая статистика
        total_stats = {
            "installs": sum(d["installs"] for d in daily_stats.values()),
            "removes": sum(d["removes"] for d in daily_stats.values()),
            "services": sum(d["services"] for d in daily_stats.values()),
            "problems": sum(d["problems"] for d in daily_stats.values())
        }
        
        return {
            "user": {
                "id": user.id,
                "name": user.full_name,
                "telegram_id": user.telegram_id
            },
            "period": {
                "days": days,
                "from": date_from.strftime("%Y-%m-%d"),
                "to": datetime.now().strftime("%Y-%m-%d")
            },
            "total": total_stats,
            "daily": daily_stats,
            "average_per_day": {
                "operations": sum(total_stats.values()) / days
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate operator performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Экспорт роутера
__all__ = ['router']