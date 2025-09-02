# app/core/database.py
from typing import Optional, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from loguru import logger
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from app.core.config import settings
from app.models.base import Base
from app.models.user import User, AccessToken


# --- 1. 全局变量定义 ---
_engine: Optional[AsyncEngine] = None
_SessionFactory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("数据库引擎未初始化. 请先调用 setup_database_connection")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _SessionFactory is None:
        raise RuntimeError("会话工厂未初始化. 请先调用 setup_database_connection")
    return _SessionFactory


# --- 2. 通用的数据库初始化和关闭函数 ---
async def setup_database_connection():
    """
    初始化全局的数据库引擎和会话工厂。
    """
    global _engine, _SessionFactory
    if _engine is not None:
        logger.info("数据库已初始化，跳过重复设置。")
        return

    # 针对不同 DB_TYPE 定制参数
    engine_options = settings.SQLALCHEMY_ENGINE_OPTIONS.copy()
    if settings.DB_TYPE == "postgres":
        engine_options["pool_pre_ping"] = True  # 适合长连接场景
    elif settings.DB_TYPE == "sqlite":
        # SQLite 不支持连接池参数，确保不会传 pool_pre_ping
        engine_options.pop("pool_pre_ping", None)

    # 创建异步引擎
    _engine = create_async_engine(
        settings.DATABASE_URL,
        **engine_options,
    )

    # 创建会话工厂
    _SessionFactory = async_sessionmaker(
        class_=AsyncSession, expire_on_commit=False, bind=_engine
    )
    logger.info(f"数据库引擎和会话工厂已创建: {settings.DB_TYPE}")


async def close_database_connection():
    """
    关闭全局的数据库引擎连接池。
    这是一个通用的关闭函数，可以在 FastAPI 关闭时调用。
    """
    global _engine, _SessionFactory
    if _engine:
        await _engine.dispose()
        _engine = None  # 清理引用
        _SessionFactory = None  # 清理引用
        logger.info("数据库引擎连接池已关闭。")


# --- 3. 依赖注入函数 ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    为每个请求或任务提供数据库会话。
    它现在依赖由 setup_database_connection 管理的全局 SessionFactory。
    """
    if _SessionFactory is None:
        # 这个错误通常不应该在正确配置的生产环境中出现
        # 它表明 setup_database_connection 未在应用启动时调用
        raise Exception("数据库未初始化。请检查 FastAPI 的 lifespan 启动配置。")

    async with _SessionFactory() as session:
        yield session


# --- 4. 数据库表创建工具 ---
async def create_db_and_tables():
    if not _engine:
        raise Exception("无法创建表，因为数据库引擎未初始化。")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建成功。")
        
        
# --- 5. FastAPI Users 专用 ---
async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)
    
async def get_access_token_db(
    session: AsyncSession = Depends(get_db),
):  
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
