# 📘 FastAPI Users Template

一个开箱即用的 **FastAPI 用户认证模板** 🚀，内置 [FastAPI Users](https://fastapi-users.github.io/) 集成，支持 **PostgreSQL 与 SQLite 双数据库**，适合作为学习示例或生产级微服务的起点。

---

## ✨ 特性

* ✅ **双数据库支持**：通过 `.env` 一键切换 Postgres / SQLite
* ✅ **完整用户认证**：注册、登录、验证、重置密码、用户管理
* ✅ **JWT 认证**：内置 Database Strategy，支持 Token 存储与过期控制
* ✅ **数据库抽象**：SQLAlchemy + Async，自动建表
* ✅ **时间戳混入 (DateTimeMixin)**：自动维护 `created_at` / `updated_at` 字段，兼容 Postgres & SQLite，无需人工干预
* ✅ **健康检查**：内置 `/health`、`/db-check`
* ✅ **可扩展架构**：清晰的 `core / models / schemas` 分层

---

## 📂 目录结构

```
app/
  core/          # 配置、数据库、用户管理器
  models/        # SQLAlchemy 模型 (User / AccessToken)
    mixin.py     # 提供 DateTimeMixin，可复用到任意模型
  schemas/       # Pydantic 模型 (UserRead / Create / Update)
  lifespan.py    # 应用生命周期钩子 (启动/关闭)
  main.py        # FastAPI 入口
.env.example     # 环境变量示例
pyproject.toml   # 项目依赖
```

---

## ⚙️ 安装与运行

### 1️⃣ 克隆仓库

```bash
git clone https://github.com/yourname/users-template.git
cd users-template
```

### 2️⃣ 安装依赖

```bash
uv sync   # 推荐使用 uv (Python 包管理器)
# 或者
pip install -e .
```

### 3️⃣ 配置环境变量

复制 `.env.example` 为 `.env` 并修改：

```bash
cp .env.example .env
```

* 使用 **PostgreSQL**

  ```env
  DB_TYPE=postgres
  DB_HOST=localhost
  DB_PORT=5432
  DB_USER=postgres
  DB_PASSWORD=postgres
  DB_NAME=fastapi_users
  ```

* 使用 **SQLite**

  ```env
  DB_TYPE=sqlite
  SQLITE_PATH=./db.sqlite3
  ```

### 4️⃣ 启动服务

```bash
uvicorn app.main:app --reload
```

访问 👉 [http://localhost:8000/docs](http://localhost:8000/docs) 查看交互式 API 文档。

---

## 🔑 API 路由

| 路径                      | 方法   | 描述        |
| ----------------------- | ---- | --------- |
| `/auth/jwt/login`       | POST | 登录获取 JWT  |
| `/auth/register`        | POST | 注册用户      |
| `/auth/forgot-password` | POST | 忘记密码      |
| `/auth/reset-password`  | POST | 重置密码      |
| `/auth/verify`          | POST | 邮箱验证      |
| `/users/{id}`           | GET  | 获取用户信息    |
| `/authenticated-route`  | GET  | 示例需要登录的路由 |
| `/health`               | GET  | 健康检查      |
| `/db-check`             | GET  | 数据库连通性检查  |

---

## 🕒 使用 DateTimeMixin（自动时间戳）

本项目预置了一个 `DateTimeMixin`，可添加到任意模型中：

```python
# app/models/mixin.py
from app.models.mixin import DateTimeMixin
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Article(DateTimeMixin, Base):
    __tablename__ = "article"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
```

效果：

* 新增记录时自动写入 `created_at`、`updated_at`
* 更新记录时自动刷新 `updated_at`
* 在 **Postgres** 使用 `server_default=func.now()` / `onupdate=func.now()`
* 在 **SQLite** 自动退化为 Python 应用层的 `datetime.utcnow`

无需人工干预，保证两种数据库行为一致。

---

## 🛠️ 技术栈

* [FastAPI](https://fastapi.tiangolo.com/)
* [FastAPI Users](https://fastapi-users.github.io/)
* [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/)
* [PostgreSQL + asyncpg](https://magicstack.github.io/asyncpg/current/)
* [SQLite + aiosqlite](https://aiosqlite.omnilib.dev/en/stable/)
* [Pydantic v2 + pydantic-settings](https://docs.pydantic.dev/latest/)
* [Loguru](https://github.com/Delgan/loguru)

---

## 🚀 扩展方向

* 集成 **OAuth2 / 社交登录 (Google, GitHub)**
* 支持 **Redis 作为 Session 存储**
* 使用 **Docker Compose** 一键启动 (FastAPI + Postgres + Adminer)
* 提供 **前端示例** (React / Vue 登录表单)

---
## 📬 联系

* 微信公众号：**码间絮语**
<center>
  <img src="https://github.com/acelee0621/fastapi-users-turtorial/blob/main/QRcode.png" width="500" alt="签名图">
</center>

* 欢迎 Star ⭐ & 关注，获取最新教程和代码更新。

## 📜 License

MIT © 2025 Aaron Lee
