import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class Settings:
    """应用配置类"""
    
    # 环境配置
    environment: str = os.getenv('ENVIRONMENT', 'development')
    database_sync_mode: str = os.getenv('DATABASE_SYNC_MODE', 'auto')
    
    # 数据库配置
    postgres_host: Optional[str] = os.getenv('POSTGRES_HOST')
    postgres_port: Optional[str] = os.getenv('POSTGRES_PORT')
    postgres_db: Optional[str] = os.getenv('POSTGRES_DB')
    postgres_user: Optional[str] = os.getenv('POSTGRES_USER')
    postgres_password: Optional[str] = os.getenv('POSTGRES_PASSWORD')
    postgres_sslmode: str = os.getenv('POSTGRES_SSLMODE', 'prefer')
    
    # LLM配置
    openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    openai_base_url: str = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    anthropic_base_url: str = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1')
    anthropic_model: str = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
    default_llm_model: str = os.getenv('DEFAULT_LLM_MODEL', 'gpt-3.5-turbo')
    default_llm_temperature: float = float(os.getenv('DEFAULT_LLM_TEMPERATURE', '0.7'))
    default_llm_max_tokens: int = int(os.getenv('DEFAULT_LLM_MAX_TOKENS', '1000'))
    
    # LLM重试配置
    llm_max_retries_primary: int = int(os.getenv('LLM_MAX_RETRIES_PRIMARY', '1'))
    llm_max_retries_fallback: int = int(os.getenv('LLM_MAX_RETRIES_FALLBACK', '1'))
    llm_retry_delay_seconds: float = float(os.getenv('LLM_RETRY_DELAY_SECONDS', '1.0'))
    
    # LLM内容过滤配置
    llm_content_filter_error_code: str = os.getenv('LLM_CONTENT_FILTER_ERROR_CODE', '1301')
    llm_content_filter_error_field: str = os.getenv('LLM_CONTENT_FILTER_ERROR_FIELD', 'contentFilter')
    
    # 日志配置
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # RAG配置
    rag_model_name: str = os.getenv('RAG_MODEL_NAME', 'Qwen/Qwen3-Embedding-0.6B')
    rag_vector_dim: int = int(os.getenv('RAG_VECTOR_DIM', '1024'))
    rag_chunk_size: int = int(os.getenv('RAG_CHUNK_SIZE', '500'))
    rag_chunk_overlap: int = int(os.getenv('RAG_CHUNK_OVERLAP', '50'))
    rag_max_tokens: int = int(os.getenv('RAG_MAX_TOKENS', '4000'))
    rag_top_k: int = int(os.getenv('RAG_TOP_K', '10'))
    use_gpu: bool = os.getenv('USE_GPU', 'false').lower() == 'true'
    rag_device: str = os.getenv('RAG_DEVICE', 'cpu')
    search_max_results: int = int(os.getenv('SEARCH_MAX_RESULTS', '20'))
    search_region: str = os.getenv('SEARCH_REGION', 'cn-zh')
    # 数据库URL可复用sqlalchemy_database_url
    
    @property
    def sqlalchemy_database_url(self) -> str:
        """获取数据库URL"""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?sslmode={self.postgres_sslmode}"
        )


# 全局设置实例
_settings = None


def get_settings() -> Settings:
    """获取应用设置"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# 向后兼容的变量
settings = get_settings()
ENVIRONMENT = settings.environment
DATABASE_SYNC_MODE = settings.database_sync_mode
POSTGRES_HOST = settings.postgres_host
POSTGRES_PORT = settings.postgres_port
POSTGRES_DB = settings.postgres_db
POSTGRES_USER = settings.postgres_user
POSTGRES_PASSWORD = settings.postgres_password
POSTGRES_SSLMODE = settings.postgres_sslmode
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
DATABASE_URL = SQLALCHEMY_DATABASE_URL
LOG_LEVEL = settings.log_level

# LLM配置变量
OPENAI_API_KEY = settings.openai_api_key
ANTHROPIC_API_KEY = settings.anthropic_api_key
OPENAI_BASE_URL = settings.openai_base_url
ANTHROPIC_BASE_URL = settings.anthropic_base_url
ANTHROPIC_MODEL = settings.anthropic_model
DEFAULT_LLM_MODEL = settings.default_llm_model
DEFAULT_LLM_TEMPERATURE = settings.default_llm_temperature
DEFAULT_LLM_MAX_TOKENS = settings.default_llm_max_tokens 

# RAG配置变量
RAG_MODEL_NAME = settings.rag_model_name
RAG_VECTOR_DIM = settings.rag_vector_dim
RAG_CHUNK_SIZE = settings.rag_chunk_size
RAG_CHUNK_OVERLAP = settings.rag_chunk_overlap
RAG_MAX_TOKENS = settings.rag_max_tokens
RAG_TOP_K = settings.rag_top_k
USE_GPU = settings.use_gpu
RAG_DEVICE = settings.rag_device
SEARCH_MAX_RESULTS = settings.search_max_results
SEARCH_REGION = settings.search_region 