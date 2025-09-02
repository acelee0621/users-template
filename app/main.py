# app/main.py
from fastapi import Depends, FastAPI, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.user_manager import auth_backend, get_current_user, fastapi_users
from app.models.user import User
from app.schemas.user import UserRead, UserCreate, UserUpdate

from app.core.config import Settings, get_settings, settings
from app.core.database import get_db
from app.lifespan import lifespan


app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI Users 模板",
    lifespan=lifespan,
)


# 路由引入
# FastAPI-Users 路由
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# 其他路由


@app.get("/health")
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.email}!"}



@app.get("/")
def read_root(
    # 使用 FastAPI 的依赖注入系统来获取配置实例
    # FastAPI 会自动调用 get_settings()，由于缓存的存在，这几乎没有开销
    settings: Settings = Depends(get_settings),
):
    """
    一个示例端点，演示如何访问配置。
    """
    return {
        "message": f"Hello from the {settings.APP_NAME}!",        
        "debug_mode": settings.DEBUG,        
        "database_type": settings.DB_TYPE,
        # 演示如何使用在模型中动态计算的属性
        "database_url_hidden_password": settings.DATABASE_URL.replace(
            settings.DB_PASSWORD, "****"
        )        
    }


@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    """
    一个简单的端点，用于检查数据库连接是否正常工作。
    """
    try:
        # 执行一个简单的查询来验证连接
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one() == 1:
            return {"status": "ok", "message": "数据库连接成功！"}
    except Exception as e:
        return {"status": "error", "message": f"数据库连接失败: {e}"}
