from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class DocumentORM(Base):
    __tablename__ = 'rag_documents'
    id = Column(String, primary_key=True)
    content = Column(Text)
    doc_meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    vectors = relationship('VectorORM', back_populates='document', cascade="all, delete-orphan")

class VectorORM(Base):
    __tablename__ = 'rag_vectors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey('rag_documents.id'))
    vector = Column(Vector(1024))  # 使用pgvector类型
    model_name = Column(String)
    dim = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    document = relationship('DocumentORM', back_populates='vectors') 