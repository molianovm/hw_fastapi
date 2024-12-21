import uuid
from datetime import datetime

from sqlalchemy import Integer, DECIMAL, DateTime, func, String, ForeignKey, UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from config import PG_DSN

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):

    @property
    def id_dict(self):
        return {"id": self.id}


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50),
        unique=True,
        index=True,
        nullable=False)
    password: Mapped[str] = mapped_column(String(70), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime,
        server_default=func.now(),
        onupdate=func.now())
    tokens: Mapped[list["Token"]] = relationship("Token",
        back_populates="user",
        lazy="joined")
    ads: Mapped[list["Advertisement"]] = relationship("Advertisement",
        back_populates="user",
        lazy="joined")


class Token(Base):
    __tablename__ = "token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(UUID,
        unique=True,
        server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = ForeignKey("user.id")
    user: Mapped[User] = relationship(User, back_populates="tokens", lazy="joined")

    @property
    def dict(self):
        return {"token": self.token}


class Advertisement(Base):
    __tablename__ = "advertisement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    author: Mapped[str] = ForeignKey("user.id")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now())
    user: Mapped[User] = relationship(User, back_populates="ads", lazy="joined")

    @property
    def dict(self): return {
        "id": self.id,
        "title": self.title,
        "description": self.description,
        "price": self.price,
        "author": self.author,
        "created_at": self.created_at.isoformat(),
        "updated_at": self.updated_at.isoformat(),
    }


ORM_OBJ = Advertisement | User | Token
ORM_CLS = type(Advertisement) | type(User) | type(Token)


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
