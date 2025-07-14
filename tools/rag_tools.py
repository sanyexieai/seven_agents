"""
RAG (Retrieval-Augmented Generation) 工具模块
提供文档检索、向量搜索、知识库管理等功能
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import numpy as np
from abc import ABC, abstractmethod
from config.settings import (
    RAG_MODEL_NAME, RAG_VECTOR_DIM, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP,
    RAG_MAX_TOKENS, RAG_TOP_K, USE_GPU, RAG_DEVICE, SQLALCHEMY_DATABASE_URL
)
from sqlalchemy import create_engine, Column, String, LargeBinary, JSON, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import torch
from transformers import AutoTokenizer, AutoModel
from database.rag_db import DBVectorStore
from tools.rag_types import Document, VectorStore

Base = declarative_base()

class DocumentORM(Base):
    __tablename__ = 'rag_documents'
    id = Column(String, primary_key=True)
    content = Column(Text)
    doc_meta = Column(JSON)
    vector = relationship('VectorORM', back_populates='document', uselist=False, cascade="all, delete-orphan")

class VectorORM(Base):
    __tablename__ = 'rag_vectors'
    doc_id = Column(String, ForeignKey('rag_documents.id', ondelete='CASCADE'), primary_key=True)
    vector = Column(LargeBinary)  # float32 bytes
    document = relationship('DocumentORM', back_populates='vector')

class SimpleVectorStore(VectorStore):
    """简单的内存向量存储实现"""
    
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self._embedding_model = None
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取文本的向量表示（简化实现）"""
        # 这里应该使用真实的embedding模型，如OpenAI的text-embedding-ada-002
        # 现在使用简单的字符频率作为向量
        char_freq = {}
        for char in text.lower():
            if char.isalpha():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # 转换为固定长度的向量
        vector = [char_freq.get(chr(i), 0) for i in range(97, 123)]  # a-z
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        # 避免除零错误
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到向量存储"""
        try:
            for doc in documents:
                self.documents[doc.doc_id] = doc
                self.embeddings[doc.doc_id] = self._get_embedding(doc.content)
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """搜索相似文档"""
        query_embedding = self._get_embedding(query)
        similarities = []
        
        for doc_id, doc_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((self.documents[doc_id], similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            del self.embeddings[doc_id]
            return True
        return False
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档"""
        return self.documents.get(doc_id)


class DocumentLoader:
    """文档加载器"""
    
    def __init__(self):
        self.supported_extensions = {'.txt', '.md', '.json', '.csv'}
    
    def load_file(self, file_path: str) -> Optional[Document]:
        """加载单个文件"""
        try:
            path = Path(file_path)
            if path.suffix.lower() not in self.supported_extensions:
                print(f"不支持的文件类型: {path.suffix}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_meta = {
                "file_path": file_path,
                "file_size": len(content),
                "file_type": path.suffix,
                "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
            
            return Document(content, doc_meta)
            
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return None
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """加载目录中的所有支持文件"""
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"目录不存在: {directory_path}")
            return documents
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                doc = self.load_file(str(file_path))
                if doc:
                    documents.append(doc)
        
        return documents


class RAGProcessor:
    """RAG处理器，所有操作走DBVectorStore"""
    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or DBVectorStore()
        self.document_loader = DocumentLoader()

    def add_documents(self, documents: List[Document]) -> bool:
        """
        批量添加文档到知识库，自动embedding并存储向量。
        :param documents: 文档列表
        :return: 添加结果
        """
        try:
            return self.vector_store.add_documents(documents)
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False

    def add_file(self, file_path: str) -> bool:
        doc = self.document_loader.load_file(file_path)
        if doc:
            return self.add_documents([doc])
        return False

    def add_directory(self, directory_path: str) -> bool:
        documents = self.document_loader.load_directory(directory_path)
        if documents:
            return self.add_documents(documents)
        return False

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """
        根据查询词搜索相似文档。
        :param query: 查询词
        :param top_k: 返回的相似文档数量
        :return: 文档列表及其相似度
        """
        try:
            return self.vector_store.search(query, top_k)
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def generate_response(self, query: str, context_docs: List[Document] = None) -> str:
        try:
            if context_docs is None:
                search_results = self.search(query, top_k=3)
                context_docs = [doc for doc, score in search_results]
            context = "\n\n".join([doc.content for doc in context_docs])
            return f"""基于检索到的信息，回答您的问题：\n\n问题：{query}\n\n相关文档内容：\n{context}\n\n回答：根据以上信息，我可以为您提供相关的回答。这是一个基于RAG生成的回答示例。"""
        except Exception as e:
            return f"RAG生成回答失败: {e}"

    def get_knowledge_stats(self) -> Dict[str, Any]:
        try:
            # 只统计文档数量
            if hasattr(self.vector_store, 'Session'):
                session = self.vector_store.Session()
                try:
                    total_documents = session.query(self.vector_store.DocumentORM).count()
                finally:
                    session.close()
                return {
                    "total_documents": total_documents,
                    "storage_type": "database",
                    "last_updated": datetime.now().isoformat()
                }
            return {"error": "未知的存储类型"}
        except Exception as e:
            return {"error": str(e)}

class RAGTool:
    """RAG工具类，面向业务接口"""
    def __init__(self, knowledge_base_path: str = "./data/documents"):
        self.knowledge_base_path = knowledge_base_path
        self.rag_processor = RAGProcessor()
        self._load_existing_knowledge()

    def _load_existing_knowledge(self):
        # 可选：首次加载本地目录到知识库
        if os.path.exists(self.knowledge_base_path):
            self.rag_processor.add_directory(self.knowledge_base_path)

    def search_knowledge(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        results = self.rag_processor.search(query, top_k)
        return {
            "query": query,
            "results": [
                {
                    "doc_id": doc.doc_id,
                    "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "doc_meta": doc.doc_meta,
                    "similarity": float(score)
                }
                for doc, score in results
            ],
            "total_results": len(results)
        }

    def add_document(self, content: str, doc_meta: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        添加单条文档到知识库，自动embedding并存储向量。
        :param content: 文档内容
        :param doc_meta: 文档元数据
        :return: 添加结果
        """
        doc = Document(content, doc_meta)
        success = self.rag_processor.add_documents([doc])
        return {
            "success": success,
            "doc_id": doc.doc_id,
            "message": "文档添加成功" if success else "文档添加失败"
        }

    def add_documents(self, contents: List[str], doc_metas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量添加多条文档到知识库。
        :param contents: 文档内容列表
        :param doc_metas: 文档元数据列表
        :return: 每条文档的添加结果
        """
        results = []
        for content, doc_meta in zip(contents, doc_metas):
            results.append(self.add_document(content, doc_meta))
        return results

    def generate_answer(self, question: str) -> Dict[str, Any]:
        try:
            answer = self.rag_processor.generate_response(question)
            return {
                "success": True,
                "question": question,
                "answer": answer
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_knowledge_stats(self) -> Dict[str, Any]:
        return self.rag_processor.get_knowledge_stats()


# 全局RAG工具实例
rag_tool = RAGTool() 