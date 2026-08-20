from sqlalchemy import Column, BigInteger, String, Boolean, JSON, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

async_session = async_sessionmaker(engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    dialogue = Column(JSON, nullable=True, default=lambda: [{"role": "system", "content": "Привет! Ты ИИ чат-бот Nestra в Telegram. Ты умеешь отвечать на текст и анализировать картинки и файлы, которые тебе присылают. Не используй Markdown-разметку (звёздочки, решётки и т.д.) — она не отображается в Telegram."}])
    ai = Column(String(50), default="anthropic/claude-3-haiku")
    privilege = Column(String(50), nullable=True, default=None)

async def user_register(user_id: int):
    """Добавление юзера в бд"""
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            new_user = User(user_id=user_id)
            session.add(new_user)
            await session.commit()
            return True
        return False


async def is_user_registered(user_id: int):
    """Функция проверки юзера в базе"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            return True
        return False


async def view_dialogue(user_id: int):
    """Функция достает диалог из бд"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            return user.dialogue
        return False


async def add_dialogue(user_id, user_dialogue):
    """Функция добавления диалога в бд"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.dialogue = user_dialogue
            await session.commit()
            return True
        return False


async def view_ai(user_id: int):
    """Функция достает значение ai из бд"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            return user.ai
        return False


async def add_ai(user_id, user_ai):
    """Функция меняет значение ai"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.ai = user_ai
            await session.commit()
            return True
        return False


async def init_db():
    """Асинхронная инициализация базы"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
