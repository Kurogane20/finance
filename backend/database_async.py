import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Get database URL from environment variable
# Assuming the same DB, but with async driver
# Convert sqlite:///./finance.db -> sqlite+aiosqlite:///./finance.db
# Convert mysql+pymysql://... -> mysql+aiomysql://...

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./finance.db")

# Automatically switch driver if needed for common cases
if "sqlite" in DATABASE_URL and "+aiosqlite" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")
elif "mysql" in DATABASE_URL and "+aiomysql" not in DATABASE_URL and "+asyncmy" not in DATABASE_URL:
    # Default to aiomysql if standard mysql url is provided
    if "+pymysql" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("+pymysql", "+aiomysql")
    else:
        DATABASE_URL = DATABASE_URL.replace("mysql:", "mysql+aiomysql:")

# Configure Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# Async Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_async_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
