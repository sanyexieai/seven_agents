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


class Document:
    """文档类"""
    
    def __init__(self, content: str, metadata: Dict[str, Any] = None, doc_id: str = None):
        self.content = content
        self.metadata = metadata or {}
        self.doc_id = doc_id or self._generate_id()
        self.created_at = datetime.now()
    
    def _generate_id(self) -> str:
        """生成文档ID"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"doc_{content_hash[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class VectorStore(ABC):
    """向量存储基类"""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到向量存储"""
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """搜索相似文档"""
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档"""
        pass


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
            
            metadata = {
                "file_path": file_path,
                "file_size": len(content),
                "file_type": path.suffix,
                "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
            
            return Document(content, metadata)
            
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
    """RAG处理器"""
    
    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or SimpleVectorStore()
        self.document_loader = DocumentLoader()
    
    def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到知识库"""
        return self.vector_store.add_documents(documents)
    
    def add_file(self, file_path: str) -> bool:
        """添加单个文件到知识库"""
        doc = self.document_loader.load_file(file_path)
        if doc:
            return self.vector_store.add_documents([doc])
        return False
    
    def add_directory(self, directory_path: str) -> bool:
        """添加目录中的所有文件到知识库"""
        documents = self.document_loader.load_directory(directory_path)
        if documents:
            return self.vector_store.add_documents(documents)
        return False
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """搜索相关文档"""
        return self.vector_store.search(query, top_k)
    
    def generate_response(self, query: str, context_docs: List[Document] = None) -> str:
        """基于检索结果生成回答"""
        if context_docs is None:
            # 自动检索相关文档
            search_results = self.search(query, top_k=3)
            context_docs = [doc for doc, score in search_results]
        
        # 构建上下文
        context = "\n\n".join([doc.content for doc in context_docs])
        
        # 这里应该调用LLM生成回答
        # 现在返回简单的模板回答
        return f"""基于检索到的信息，回答您的问题：

问题：{query}

相关文档内容：
{context}

回答：根据以上信息，我可以为您提供相关的回答。这是一个基于RAG生成的回答示例。"""
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        if isinstance(self.vector_store, SimpleVectorStore):
            return {
                "total_documents": len(self.vector_store.documents),
                "storage_type": "memory",
                "last_updated": datetime.now().isoformat()
            }
        return {"error": "未知的存储类型"}


class RAGTool:
    """RAG工具类"""
    
    def __init__(self, knowledge_base_path: str = "./data/documents"):
        self.knowledge_base_path = knowledge_base_path
        self.rag_processor = RAGProcessor()
        self._load_existing_knowledge()
    
    def _load_existing_knowledge(self):
        """加载现有的知识库"""
        if os.path.exists(self.knowledge_base_path):
            self.rag_processor.add_directory(self.knowledge_base_path)
    
    def search_knowledge(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """搜索知识库"""
        results = self.rag_processor.search(query, top_k)
        return {
            "query": query,
            "results": [
                {
                    "doc_id": doc.doc_id,
                    "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "metadata": doc.metadata,
                    "similarity": float(score)
                }
                for doc, score in results
            ],
            "total_results": len(results)
        }
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """添加文档到知识库"""
        doc = Document(content, metadata)
        success = self.rag_processor.add_documents([doc])
        return {
            "success": success,
            "doc_id": doc.doc_id,
            "message": "文档添加成功" if success else "文档添加失败"
        }
    
    def generate_answer(self, question: str) -> Dict[str, Any]:
        """生成回答"""
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
        """获取知识库统计"""
        return self.rag_processor.get_knowledge_stats()


# 全局RAG工具实例
rag_tool = RAGTool() 