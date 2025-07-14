"""
RAG工具模块的单元测试
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.rag_tools import (
    Document, VectorStore, SimpleVectorStore, DocumentLoader,
    RAGProcessor, RAGTool
)


class TestDocument(unittest.TestCase):
    """测试文档类"""
    
    def test_document_initialization(self):
        """测试文档初始化"""
        content = "测试文档内容"
        doc_meta = {"source": "test", "author": "tester"}
        doc = Document(content, doc_meta)
        
        self.assertEqual(doc.content, content)
        self.assertEqual(doc.doc_meta, doc_meta)
        self.assertIsNotNone(doc.doc_id)
        self.assertIsNotNone(doc.created_at)
    
    def test_document_with_custom_id(self):
        """测试自定义ID的文档"""
        doc = Document("测试内容", doc_id="custom_id_123")
        self.assertEqual(doc.doc_id, "custom_id_123")
    
    def test_document_to_dict(self):
        """测试文档转字典"""
        doc = Document("测试内容", {"source": "test"})
        doc_dict = doc.to_dict()
        
        self.assertIn("doc_id", doc_dict)
        self.assertIn("content", doc_dict)
        self.assertIn("doc_meta", doc_dict)
        self.assertIn("created_at", doc_dict)
        self.assertEqual(doc_dict["content"], "测试内容")
        self.assertEqual(doc_dict["doc_meta"], {"source": "test"})


class TestSimpleVectorStore(unittest.TestCase):
    """测试简单向量存储"""
    
    def setUp(self):
        self.vector_store = SimpleVectorStore()
    
    def test_add_documents(self):
        """测试添加文档"""
        doc1 = Document("第一个文档")
        doc2 = Document("第二个文档")
        
        success = self.vector_store.add_documents([doc1, doc2])
        
        self.assertTrue(success)
        self.assertIn(doc1.doc_id, self.vector_store.documents)
        self.assertIn(doc2.doc_id, self.vector_store.documents)
        self.assertIn(doc1.doc_id, self.vector_store.embeddings)
        self.assertIn(doc2.doc_id, self.vector_store.embeddings)
    
    def test_search_documents(self):
        """测试搜索文档"""
        # 添加测试文档
        doc1 = Document("人工智能技术")
        doc2 = Document("机器学习算法")
        doc3 = Document("数据库系统")
        
        self.vector_store.add_documents([doc1, doc2, doc3])
        
        # 搜索相关文档
        results = self.vector_store.search("人工智能", top_k=2)
        
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 2)
        
        for doc, score in results:
            self.assertIsInstance(doc, Document)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_delete_document(self):
        """测试删除文档"""
        doc = Document("测试文档")
        self.vector_store.add_documents([doc])
        
        # 验证文档已添加
        self.assertIn(doc.doc_id, self.vector_store.documents)
        
        # 删除文档
        success = self.vector_store.delete_document(doc.doc_id)
        
        self.assertTrue(success)
        self.assertNotIn(doc.doc_id, self.vector_store.documents)
        self.assertNotIn(doc.doc_id, self.vector_store.embeddings)
    
    def test_delete_nonexistent_document(self):
        """测试删除不存在的文档"""
        success = self.vector_store.delete_document("nonexistent_id")
        self.assertFalse(success)
    
    def test_get_document(self):
        """测试获取文档"""
        doc = Document("测试文档")
        self.vector_store.add_documents([doc])
        
        retrieved_doc = self.vector_store.get_document(doc.doc_id)
        self.assertEqual(retrieved_doc, doc)
    
    def test_get_nonexistent_document(self):
        """测试获取不存在的文档"""
        doc = self.vector_store.get_document("nonexistent_id")
        self.assertIsNone(doc)
    
    def test_cosine_similarity(self):
        """测试余弦相似度计算"""
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        vec3 = [1, 0, 0]
        
        # 正交向量相似度应该为0
        similarity1 = self.vector_store._cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity1, 0.0, places=5)
        
        # 相同向量相似度应该为1
        similarity2 = self.vector_store._cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(similarity2, 1.0, places=5)


class TestDocumentLoader(unittest.TestCase):
    """测试文档加载器"""
    
    def setUp(self):
        self.loader = DocumentLoader()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_file_txt(self):
        """测试加载txt文件"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("测试文本内容")
        
        doc = self.loader.load_file(test_file)
        
        self.assertIsNotNone(doc)
        self.assertEqual(doc.content, "测试文本内容")
        self.assertIn("file_path", doc.doc_meta)
        self.assertIn("file_size", doc.doc_meta)
        self.assertEqual(doc.doc_meta["file_type"], ".txt")
    
    def test_load_file_md(self):
        """测试加载markdown文件"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "test.md")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# 测试标题\n\n测试内容")
        
        doc = self.loader.load_file(test_file)
        
        self.assertIsNotNone(doc)
        self.assertEqual(doc.content, "# 测试标题\n\n测试内容")
        self.assertEqual(doc.doc_meta["file_type"], ".md")
    
    def test_load_unsupported_file(self):
        """测试加载不支持的文件类型"""
        # 创建不支持的文件
        test_file = os.path.join(self.temp_dir, "test.xyz")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("测试内容")
        
        doc = self.loader.load_file(test_file)
        self.assertIsNone(doc)
    
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        doc = self.loader.load_file("nonexistent_file.txt")
        self.assertIsNone(doc)
    
    def test_load_directory(self):
        """测试加载目录"""
        # 创建多个测试文件
        files = [
            ("test1.txt", "文件1内容"),
            ("test2.md", "文件2内容"),
            ("test3.json", '{"key": "value"}'),
            ("test4.xyz", "不支持的文件")
        ]
        
        for filename, content in files:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        documents = self.loader.load_directory(self.temp_dir)
        
        # 应该只加载支持的文件类型
        self.assertEqual(len(documents), 3)
        
        # 检查文件内容
        contents = [doc.content for doc in documents]
        self.assertIn("文件1内容", contents)
        self.assertIn("文件2内容", contents)
        self.assertIn('{"key": "value"}', contents)
    
    def test_load_nonexistent_directory(self):
        """测试加载不存在的目录"""
        documents = self.loader.load_directory("nonexistent_directory")
        self.assertEqual(documents, [])


class TestRAGProcessor(unittest.TestCase):
    """测试RAG处理器"""
    
    def setUp(self):
        self.rag_processor = RAGProcessor()
    
    def test_add_documents(self):
        """测试添加文档"""
        doc1 = Document("人工智能技术")
        doc2 = Document("机器学习算法")
        
        success = self.rag_processor.add_documents([doc1, doc2])
        self.assertTrue(success)
    
    def test_add_file(self):
        """测试添加文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试文件内容")
            file_path = f.name
        
        try:
            success = self.rag_processor.add_file(file_path)
            self.assertTrue(success)
        finally:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_search(self):
        """测试搜索"""
        # 添加测试文档
        doc1 = Document("人工智能技术发展")
        doc2 = Document("机器学习算法应用")
        doc3 = Document("数据库系统设计")
        
        self.rag_processor.add_documents([doc1, doc2, doc3])
        
        # 搜索
        results = self.rag_processor.search("人工智能", top_k=2)
        
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 2)
        
        for doc, score in results:
            self.assertIsInstance(doc, Document)
            self.assertIsInstance(score, float)
    
    def test_generate_response(self):
        """测试生成回答"""
        # 添加测试文档
        doc = Document("人工智能是计算机科学的一个分支")
        self.rag_processor.add_documents([doc])
        
        response = self.rag_processor.generate_response("什么是人工智能？")
        
        self.assertIsInstance(response, str)
        self.assertIn("人工智能", response)
    
    def test_get_knowledge_stats(self):
        """测试获取知识库统计"""
        stats = self.rag_processor.get_knowledge_stats()
        
        self.assertIn("total_documents", stats)
        self.assertIn("storage_type", stats)
        self.assertIn("last_updated", stats)
        self.assertEqual(stats["storage_type"], "memory")


class TestRAGTool(unittest.TestCase):
    """测试RAG工具"""
    
    def setUp(self):
        self.rag_tool = RAGTool()
    
    def test_search_knowledge(self):
        """测试搜索知识库"""
        # 先添加一些文档
        self.rag_tool.add_document("人工智能技术", {"topic": "AI"})
        self.rag_tool.add_document("机器学习算法", {"topic": "ML"})
        
        # 搜索
        result = self.rag_tool.search_knowledge("人工智能", top_k=2)
        
        self.assertIn("query", result)
        self.assertIn("results", result)
        self.assertIn("total_results", result)
        self.assertEqual(result["query"], "人工智能")
        self.assertIsInstance(result["results"], list)
    
    def test_add_document(self):
        """测试添加文档"""
        result = self.rag_tool.add_document(
            "测试文档内容",
            {"source": "test", "topic": "demo"}
        )
        
        self.assertIn("success", result)
        self.assertIn("doc_id", result)
        self.assertIn("message", result)
        self.assertTrue(result["success"])
    
    def test_generate_answer(self):
        """测试生成回答"""
        # 先添加文档
        self.rag_tool.add_document("人工智能是计算机科学的一个分支")
        
        result = self.rag_tool.generate_answer("什么是人工智能？")
        
        self.assertIn("success", result)
        self.assertIn("question", result)
        self.assertIn("answer", result)
        self.assertTrue(result["success"])
        self.assertEqual(result["question"], "什么是人工智能？")
    
    def test_get_knowledge_stats(self):
        """测试获取知识库统计"""
        stats = self.rag_tool.get_knowledge_stats()
        
        self.assertIn("total_documents", stats)
        self.assertIn("storage_type", stats)
        self.assertIn("last_updated", stats)


if __name__ == '__main__':
    unittest.main() 