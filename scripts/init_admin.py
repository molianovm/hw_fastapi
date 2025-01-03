import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import ADMIN_NAME, ADMIN_PASSWORD
from utils.security import hash_password
from db import Session
from models import User


async def create_admin(session: AsyncSession, name: str, password: str):
    user = User(name=name, password=hash_password(password), role="admin")
    session.add(user)
    await session.commit()


async def main():
    async with Session() as session:
        await create_admin(session, ADMIN_NAME, ADMIN_PASSWORD)


if __name__ == "__main__":
    asyncio.run(main())
