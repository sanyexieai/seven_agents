from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib

class Document:
    """文档类"""
    def __init__(self, content: str, doc_meta: Dict[str, Any] = None, doc_id: str = None):
        self.content = content
        self.doc_meta = doc_meta or {}
        self.doc_id = doc_id or self._generate_id()
        self.created_at = datetime.now()
    def _generate_id(self) -> str:
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"doc_{content_hash[:8]}"
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "doc_meta": self.doc_meta,
            "created_at": self.created_at.isoformat()
        }

# 可选：如需接口规范可保留VectorStore基类
from abc import ABC, abstractmethod
class VectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> bool:
        pass
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        pass
    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        pass
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Document]:
        pass 