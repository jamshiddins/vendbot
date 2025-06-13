"""
Initialize database
"""
import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import init_db, engine
from config.settings import settings
from src.db.models.user import User, UserRole
from src.db.repositories.user import UserRepository
from config.database import async_session_maker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user():
    """Create admin user if not exists"""
    async with async_session_maker() as session:
        repo = UserRepository(session)
        
        # Check if admin exists
        admin_ids = settings.admin_ids
        if admin_ids:
            admin_id = admin_ids[0]
            user = await repo.get_by_telegram_id(admin_id)
            
            if not user:
                logger.info(f"Creating admin user with ID {admin_id}")
                await repo.create(
                    telegram_id=admin_id,
                    full_name="Administrator",
                    username="admin",
                    role=UserRole.ADMIN
                )
                logger.info("Admin user created")
            else:
                logger.info("Admin user already exists")


async def main():
    """Initialize database"""
    try:
        logger.info("Initializing database...")
        await init_db()
        
        logger.info("Creating admin user...")
        await create_admin_user()
        
        logger.info("Database initialization completed!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())