from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.rag_models import Base, DocumentORM, VectorORM
from config.settings import SQLALCHEMY_DATABASE_URL, RAG_MODEL_NAME, RAG_MAX_TOKENS, RAG_DEVICE, USE_GPU, DATABASE_URL
from tools.rag_types import VectorStore, Document
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Tuple, Optional

class DBVectorStore(VectorStore):
    """数据库向量存储实现，支持Qwen embedding"""
    def __init__(self, db_url=SQLALCHEMY_DATABASE_URL):
        self.engine = create_engine(db_url, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        # 加载Qwen embedding模型
        self.device = RAG_DEVICE if USE_GPU else 'cpu'
        self.tokenizer = AutoTokenizer.from_pretrained(RAG_MODEL_NAME)
        self.model = AutoModel.from_pretrained(RAG_MODEL_NAME).to(self.device)

    def _get_embedding(self, text: str) -> list:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=RAG_MAX_TOKENS)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            emb = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        return emb.tolist()

    def add_documents(self, documents: List[Document]) -> bool:
        session = self.Session()
        try:
            for doc in documents:
                doc_orm = DocumentORM(id=doc.doc_id, content=doc.content, doc_meta=doc.doc_meta)
                session.merge(doc_orm)
                emb = self._get_embedding(doc.content)
                vec_orm = VectorORM(
                    doc_id=doc.doc_id,
                    vector=emb,  # 直接存list/np.array，pgvector自动处理
                    model_name=RAG_MODEL_NAME,
                    dim=len(emb)
                )
                session.merge(vec_orm)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"添加文档失败: {e}")
            return False
        finally:
            session.close()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        session = self.Session()
        try:
            query_emb = np.array(self._get_embedding(query), dtype=np.float32)
            vectors = session.query(VectorORM).all()
            docs = {d.id: d for d in session.query(DocumentORM).all()}
            sims = []
            for v in vectors:
                vec = np.array(v.vector, dtype=np.float32)  # 直接转np.array
                if vec.shape[0] != query_emb.shape[0]:
                    continue
                sim = float(np.dot(query_emb, vec) / (np.linalg.norm(query_emb) * np.linalg.norm(vec) + 1e-8))
                doc = docs.get(v.doc_id)
                if doc:
                    doc_obj = Document(doc.content, doc.doc_meta, doc_id=doc.id)
                    sims.append((doc_obj, sim))
            sims.sort(key=lambda x: x[1], reverse=True)
            return sims[:top_k]
        except Exception as e:
            print(f"向量检索失败: {e}")
            return []
        finally:
            session.close()

    def delete_document(self, doc_id: str) -> bool:
        session = self.Session()
        try:
            session.query(VectorORM).filter_by(doc_id=doc_id).delete()
            session.query(DocumentORM).filter_by(id=doc_id).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"删除文档失败: {e}")
            return False
        finally:
            session.close()

    def get_document(self, doc_id: str) -> Optional[Document]:
        session = self.Session()
        try:
            doc = session.query(DocumentORM).filter_by(id=doc_id).first()
            if doc:
                return Document(doc.content, doc.doc_meta, doc_id=doc.id)
            return None
        finally:
            session.close()

class DBVectorStoreSync:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def sync_database(self):
        """自动同步数据库结构（开发环境用）"""
        Base.metadata.create_all(self.engine)

# 单例

db_sync = DBVectorStoreSync() 