from sqlalchemy import BigInteger, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime

class BaseModel(DeclarativeBase, AsyncAttrs):
    created: Mapped[datetime] = mapped_column(default=datetime.now())
    updated: Mapped[datetime] = mapped_column(onupdate=datetime.now(), default=datetime.now())

class User(BaseModel):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(32), nullable=True)
    banned: Mapped[bool] = mapped_column(default=False)
    can_create_links: Mapped[bool] = mapped_column(default=False)

class Request(BaseModel):
    __tablename__ = 'requests'
    request_id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True)
    caption: Mapped[str] = mapped_column(String(1024), nullable=True)
    departure_value: Mapped[str] = mapped_column(String(256), nullable=True)
    destination_value: Mapped[str] = mapped_column(String(256), nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    key: Mapped[str] = mapped_column(String(16), nullable=True)

class Key(BaseModel):
    __tablename__ = 'keys'
    key: Mapped[str] = mapped_column(String(40), primary_key=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)

class ChatMessage(BaseModel):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    message_id: Mapped[int] = mapped_column()
    chat_id: Mapped[int] = mapped_column(BigInteger)