from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AgentModel(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    key = Column(String(64), unique=True, nullable=False)  # 添加唯一key字段
    name = Column(String(64), nullable=False)
    type = Column(String(32), nullable=False)
    description = Column(Text)
    config = Column(JSON)
    enabled = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)