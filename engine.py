import secrets

from sqlalchemy import select, update, or_, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from aiogram.types import Message
from sqlalchemy.engine import URL
from scheme import BaseModel, User, Request, ChatMessage, Key
from typing import Sequence



class DataBase:
    def __init__(self, database_url: URL):
        self.engine: AsyncEngine = create_async_engine(url=database_url)
        self.session = async_sessionmaker(bind=self.engine, expire_on_commit=False, class_=AsyncSession)

    async def process_scheme(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def get_user(self, user_id: int) -> User:
        async with self.session() as session:
            return await session.scalar(select(User).where(User.user_id == user_id))

    async def get_users(self) -> Sequence[User]:
        async with self.session() as session:
            return (await session.scalars(select(User))).all()

    async def get_users_ids(self) -> Sequence[int]:
        async with self.session() as session:
            return (await session.scalars(select(User.user_id))).all()

    async def add_user(self, message: Message) -> None:
        async with self.session() as session:
            if message.chat.id in await self.get_users_ids():
                await session.execute(update(User).where(User.user_id == message.chat.id).values(
                    username=message.chat.username, first_name=message.chat.first_name))
                try:
                    await session.commit()
                except Exception:
                    await session.rollback()
                return
            user = User(user_id=message.chat.id, username=message.chat.username, first_name=message.chat.first_name)
            session.add(user)
            try:
                await session.commit()
            except Exception:
                await session.rollback()

    async def update_user_status(self, user_id: int, status: bool) -> None:
        async with self.session() as session:
            await session.execute(update(User).where(User.user_id == user_id).values(banned=status))
            try:
                await session.commit()
            except Exception:
                await session.rollback()

    async def find_user(self, text: str) -> User | None:
        async with self.session() as session:
            try:
                text = int(text)
                return await session.scalar(select(User).where(User.user_id == text))
            except ValueError:
                return await session.scalar(select(User).where(or_(User.username == text, User.first_name == text)))

    async def add_message(self, message_id: int, chat_id: int) -> None:
        async with self.session() as session:
            session.add(ChatMessage(message_id=message_id, chat_id=chat_id))
            try:
                await session.commit()
            except Exception:
                await session.rollback()

    async def get_messages(self, chat_id: int) -> Sequence[ChatMessage]:
        async with self.session() as session:
            return (await session.scalars(select(ChatMessage).where(ChatMessage.chat_id == chat_id))).all()

    async def delete_message(self, id_: int) -> None:
        async with self.session() as session:
            await session.execute(delete(ChatMessage).where(ChatMessage.id == id_))
            try:
                await session.commit()
            except Exception:
                await session.rollback()

    async def add_request(self, caption: str, departure_value: str, destination_value: str, price: float,
                          key: str | None = None) -> Request:
        async with self.session() as session:
            request = Request(caption=caption, key=key, departure_value=departure_value, price=price,
                              destination_value=destination_value)
            session.add(request)
            try:
                await session.flush()
                await session.refresh(request)
                await session.commit()
                return request
            except Exception:
                await session.rollback()

    async def get_requests_by_key(self, key: str) -> Sequence[Request]:
        async with self.session() as session:
            return (await session.scalars(select(Request).where(Request.key == key).order_by(Request.price))).all()

    async def get_requests(self) -> Sequence[Request]:
        async with self.session() as session:
            return (await session.scalars(select(Request))).all()

    async def get_user_keys(self, user_id: int) -> Sequence[Key]:
        async with self.session() as session:
            return (await session.scalars(select(Key).where(Key.owner_id == user_id))).all()

    async def get_key(self, user_id: int | None = None, key: str | None = None) -> Key | None:
        async with self.session() as session:
            if user_id:
                return await session.scalar(select(Key).where(Key.owner_id == user_id))
            if key:
                return await session.scalar(select(Key).where(Key.key == key))

    async def get_keys(self):
        async with self.session() as session:
            return (await session.scalars(select(Key))).all()

    async def user_can_create_links(self, user_id: int, status: bool) -> None:
        async with self.session() as session:
            await session.execute(update(User).where(User.user_id == user_id).values(can_create_links=status))
            try:
                await session.commit()
            except Exception:
                await session.rollback()

    async def delete_keys(self, user_id: int) -> None:
        async with self.session() as session:
            await session.execute(delete(Key).where(Key.owner_id == user_id))
            try:
                await session.commit()
            except Exception:
                await session.rollback()

    async def add_key(self, owner_id: int):
        async with self.session() as session:
            key = secrets.token_urlsafe(16)
            session.add(Key(key=key, owner_id=owner_id))
            await session.flush()
            try:
                await session.commit()
                return key
            except Exception:
                await session.rollback()

    async def delete_key(self, key: str | None = None, owner_id: int | None = None):
        async with self.session() as session:
            await session.execute(delete(Key).where(or_(Key.key == key, Key.owner_id == owner_id)))
            try:
                await session.commit()
            except Exception:
                await session.rollback()