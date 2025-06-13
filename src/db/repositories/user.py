"""
User repository
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User, UserRole


class UserRepository:
    """Repository for user operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        telegram_id: int,
        full_name: str,
        username: Optional[str] = None,
        role: UserRole = UserRole.OPERATOR
    ) -> User:
        """Create new user"""
        user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            role=role
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update(self, user: User) -> User:
        """Update user"""
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_all_active(self) -> List[User]:
        """Get all active users"""
        result = await self.session.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()
    
    async def get_by_role(self, role: UserRole) -> List[User]:
        """Get users by role"""
        result = await self.session.execute(
            select(User).where(User.role == role, User.is_active == True)
        )
        return result.scalars().all()