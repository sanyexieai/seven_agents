import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 环境配置
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # development, production, testing
DATABASE_SYNC_MODE = os.getenv('DATABASE_SYNC_MODE', 'auto')  # auto, alembic, none

# 数据库配置
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_SSLMODE = os.getenv('POSTGRES_SSLMODE', 'prefer')

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode={POSTGRES_SSLMODE}"
)

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO') 