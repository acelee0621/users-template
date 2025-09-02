# app/lifespan.py
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.core.config import get_settings
from app.core.database import (
    setup_database_connection,
    close_database_connection,
    create_db_and_tables,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    # -------- 启动 --------
    get_settings()
    await setup_database_connection()
    logger.info("🚀 应用启动，数据库已就绪。")
    await create_db_and_tables()

    yield

    # -------- 关闭 --------
    await close_database_connection()
    logger.info("应用关闭，资源已释放。")
