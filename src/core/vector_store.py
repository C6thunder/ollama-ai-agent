"""向量存储与检索模块

实现基于语义相似度的文档检索系统（RAG）
支持多种向量存储策略和检索算法

主要功能：
1. 向量化文档
2. 存储向量和元数据
3. 语义搜索
4. 混合检索（向量 + 关键词）
5. 检索结果重排序
"""

import os
import json
import math
import pickle
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果"""

    document: Any  # Document 对象
    score: float  # 相似度分数
    metadata: Dict[str, Any]  # 元数据
    source: str  # 来源

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.document.content if hasattr(self.document, 'content') else str(self.document),
            "score": self.score,
            "metadata": self.metadata,
            "source": self.source
        }


class EmbeddingFunction(ABC):
    """向量嵌入函数基类"""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """将文本转换为向量"""
        pass

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量向量化"""
        return [self.embed(text) for text in texts]


class TFIDFEmbedding(EmbeddingFunction):
    """TF-IDF 向量嵌入（简化版）"""

    def __init__(self, vocabulary: Optional[Dict[str, int]] = None):
        self.vocabulary = vocabulary or {}
        self.doc_count = 0
        self.document_frequencies = defaultdict(int)

    def embed(self, text: str) -> List[float]:
        """TF-IDF 向量化"""
        # 简单的文本预处理
        tokens = self._tokenize(text)
        token_counts = defaultdict(int)

        # 计算词频
        for token in tokens:
            token_counts[token] += 1

        # 构建向量
        vector = [0.0] * len(self.vocabulary)
        for token, count in token_counts.items():
            if token in self.vocabulary:
                tf = count / len(tokens)
                df = self.document_frequencies[token]
                idf = math.log(self.doc_count / (df + 1))
                vector[self.vocabulary[token]] = tf * idf

        return vector

    def _tokenize(self, text: str) -> List[str]:
        """简单的分词"""
        import re
        return re.findall(r'\w+', text.lower())


class SimpleEmbedding(EmbeddingFunction):
    """简单文本哈希嵌入（用于演示）"""

    def embed(self, text: str) -> List[float]:
        """字符频率向量"""
        # 使用字符频率作为简化的 embedding
        char_set = set(text.lower())
        vector = [1.0 if c in text.lower() else 0.0 for c in 'abcdefghijklmnopqrstuvwxyz']
        return vector


class BaseVectorStore(ABC):
    """向量存储基类"""

    @abstractmethod
    def add(self, documents: List[Any], embeddings: Optional[List[List[float]]] = None):
        """添加文档"""
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """相似度搜索"""
        pass

    @abstractmethod
    def save(self, path: str):
        """保存到文件"""
        pass

    @abstractmethod
    def load(self, path: str):
        """从文件加载"""
        pass


class InMemoryVectorStore(BaseVectorStore):
    """内存向量存储"""

    def __init__(
        self,
        embedding_function: Optional[EmbeddingFunction] = None,
        dimension: int = 26  # 简单 embedding 的维度
    ):
        self.embedding_function = embedding_function or SimpleEmbedding()
        self.dimension = dimension
        self.documents = []  # 存储 Document 对象
        self.embeddings = []  # 存储向量
        self.metadatas = []  # 存储元数据
        self.ids = []  # 存储 ID

    def add(
        self,
        documents: List[Any],
        embeddings: Optional[List[List[float]]] = None
    ):
        """添加文档"""
        if embeddings is None:
            # 自动生成 embedding
            texts = [doc.content if hasattr(doc, 'content') else str(doc) for doc in documents]
            embeddings = self.embedding_function.embed_batch(texts)

        # 验证维度
        for embedding in embeddings:
            if len(embedding) != self.dimension:
                raise ValueError(f"向量维度不匹配: 期望 {self.dimension}, 得到 {len(embedding)}")

        # 添加到存储
        start_id = len(self.documents)
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            self.documents.append(doc)
            self.embeddings.append(embedding)
            self.metadatas.append(doc.metadata if hasattr(doc, 'metadata') else {})
            self.ids.append(start_id + i)

        logger.info(f"添加了 {len(documents)} 个文档，总计 {len(self.documents)} 个")

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """相似度搜索"""
        if not self.documents:
            return []

        # 查询向量
        query_embedding = self.embedding_function.embed(query)

        # 计算相似度
        scores = []
        for i, embedding in enumerate(self.embeddings):
            # 应用过滤器
            if filter and not self._match_filter(self.metadatas[i], filter):
                continue

            # 计算余弦相似度
            score = self._cosine_similarity(query_embedding, embedding)
            scores.append((i, score))

        # 排序并返回 top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for i, score in scores[:k]:
            results.append(SearchResult(
                document=self.documents[i],
                score=score,
                metadata=self.metadatas[i],
                source=self.metadatas[i].get('source', 'unknown')
            ))

        return results

    def _match_filter(self, metadata: Dict[str, Any], filter: Dict[str, Any]) -> bool:
        """检查元数据是否匹配过滤器"""
        for key, value in filter.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0
        return dot_product / (norm_a * norm_b)

    def save(self, path: str):
        """保存到文件"""
        data = {
            'documents': [doc.to_dict() if hasattr(doc, 'to_dict') else doc for doc in self.documents],
            'embeddings': self.embeddings,
            'metadatas': self.metadatas,
            'ids': self.ids,
            'dimension': self.dimension
        }

        with open(path, 'wb') as f:
            pickle.dump(data, f)

        logger.info(f"向量存储已保存到 {path}")

    def load(self, path: str):
        """从文件加载"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件不存在: {path}")

        with open(path, 'rb') as f:
            data = pickle.load(f)

        self.documents = data['documents']
        self.embeddings = data['embeddings']
        self.metadatas = data['metadatas']
        self.ids = data['ids']
        self.dimension = data.get('dimension', 26)

        logger.info(f"从 {path} 加载了 {len(self.documents)} 个文档")

    def delete(self, ids: List[str]):
        """删除文档"""
        id_set = set(ids)
        keep_indices = [i for i, doc_id in enumerate(self.ids) if doc_id not in id_set]

        self.documents = [self.documents[i] for i in keep_indices]
        self.embeddings = [self.embeddings[i] for i in keep_indices]
        self.metadatas = [self.metadatas[i] for i in keep_indices]
        self.ids = [self.ids[i] for i in keep_indices]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "document_count": len(self.documents),
            "dimension": self.dimension,
            "total_characters": sum(len(doc.content) if hasattr(doc, 'content') else 0 for doc in self.documents)
        }


class RAGSystem:
    """检索增强生成系统"""

    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_function: Optional[EmbeddingFunction] = None,
        llm: Optional[Any] = None
    ):
        self.vector_store = vector_store
        self.embedding_function = embedding_function or SimpleEmbedding()
        self.llm = llm

    def add_documents(self, documents: List[Any]):
        """添加文档到 RAG 系统"""
        self.vector_store.add(documents)

    def query(
        self,
        question: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        rerank: bool = True
    ) -> Dict[str, Any]:
        """回答问题

        Args:
            question: 问题
            k: 返回文档数量
            filter: 元数据过滤器
            rerank: 是否重排序

        Returns:
            包含问题和答案的字典
        """
        # 1. 检索相关文档
        relevant_docs = self.vector_store.similarity_search(question, k=k, filter=filter)

        if not relevant_docs:
            return {
                "question": question,
                "answer": "抱歉，没有找到相关信息",
                "context": "",
                "relevant_documents": [],
                "confidence": 0.0
            }

        # 2. 准备上下文
        context_parts = []
        for i, doc in enumerate(relevant_docs):
            doc_content = doc.document.content if hasattr(doc.document, 'content') else str(doc.document)
            doc_source = doc.source if hasattr(doc, 'source') else f"doc_{i}"
            context_parts.append(f"文档 {i+1} [{doc_source}]:\n{doc_content}")

        context = "\n\n".join(context_parts)

        # 3. 生成答案（这里使用简单模板，实际应调用 LLM）
        answer = self._generate_answer(question, context, relevant_docs)

        # 4. 计算置信度
        confidence = self._calculate_confidence(relevant_docs)

        return {
            "question": question,
            "answer": answer,
            "context": context,
            "relevant_documents": [doc.to_dict() for doc in relevant_docs],
            "confidence": confidence
        }

    def _generate_answer(
        self,
        question: str,
        context: str,
        relevant_docs: List[SearchResult]
    ) -> str:
        """生成答案"""
        # 如果有 LLM，使用 LLM 生成答案
        if self.llm is not None:
            try:
                # 记录调试信息
                logger.info(f"生成答案 - 问题: {question}")
                logger.info(f"检索到 {len(relevant_docs)} 个相关文档")
                logger.info(f"上下文长度: {len(context)} 字符")

                # 构建提示
                prompt = f"""你是一个专业的文档总结助手。请基于提供的上下文信息回答问题。

重要说明：
1. 只使用上下文信息中的内容回答问题
2. 如果上下文信息中没有相关内容，直接说明"上下文信息中没有相关内容"
3. 不要添加上下文信息中没有的内容

上下文信息：
{context}

问题：{question}

回答："""

                # 记录提示内容（前200字符）
                logger.info(f"提示内容（前200字符）: {prompt[:200]}...")

                # 调用 LLM 生成答案
                response = self.llm.invoke(prompt)

                # 获取答案内容
                if hasattr(response, 'content'):
                    answer = response.content
                elif isinstance(response, dict) and 'content' in response:
                    answer = response['content']
                else:
                    answer = str(response)

                logger.info(f"LLM 回答长度: {len(answer)} 字符")
                logger.info(f"LLM 回答: {answer[:200]}...")

                return answer.strip()

            except Exception as e:
                logger.error(f"LLM 生成答案失败: {str(e)}")
                # LLM 失败时回退到演示实现
                return f"""
基于以下 {len(relevant_docs)} 个相关文档片段的回答：

{context[:500]}...

注意：LLM 调用失败，使用演示版本。
错误信息：{str(e)}
"""
        else:
            # 没有 LLM 时使用演示实现
            return f"""
基于以下 {len(relevant_docs)} 个相关文档片段的回答：

{context[:500]}...

注意：这是演示版本，实际应用中应调用 LLM 生成答案。
"""

    def _calculate_confidence(self, relevant_docs: List[SearchResult]) -> float:
        """计算置信度"""
        if not relevant_docs:
            return 0.0

        # 基于最高分数计算置信度
        max_score = max(doc.score for doc in relevant_docs)
        avg_score = sum(doc.score for doc in relevant_docs) / len(relevant_docs)

        # 综合最高分数和平均分数
        confidence = (max_score + avg_score) / 2
        return min(max(confidence, 0.0), 1.0)

    def batch_query(
        self,
        questions: List[str],
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """批量查询"""
        return [self.query(q, k=k, filter=filter) for q in questions]

    def get_relevant_docs(
        self,
        question: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """只检索相关文档，不生成答案"""
        return self.vector_store.similarity_search(question, k=k, filter=filter)

    def save(self, path: str):
        """保存 RAG 系统"""
        self.vector_store.save(path)

    def load(self, path: str):
        """加载 RAG 系统"""
        self.vector_store.load(path)


class HybridSearch:
    """混合搜索（向量 + 关键词）"""

    def __init__(self, vector_store: BaseVectorStore):
        self.vector_store = vector_store

    def search(
        self,
        query: str,
        k: int = 5,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[SearchResult]:
        """混合搜索"""
        # 1. 向量搜索
        vector_results = self.vector_store.similarity_search(query, k=k*2)

        # 2. 关键词搜索（简化版）
        keyword_results = self._keyword_search(query, k=k*2)

        # 3. 合并结果
        combined_scores = {}
        for i, doc in enumerate(vector_results):
            doc_id = i
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + doc.score * vector_weight

        for i, doc in enumerate(keyword_results):
            doc_id = i + len(vector_results)
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + doc.score * keyword_weight

        # 4. 排序
        all_results = vector_results + keyword_results
        sorted_results = sorted(
            [(i, score) for i, score in combined_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )

        # 5. 返回 top-k
        results = []
        for doc_id, score in sorted_results[:k]:
            if doc_id < len(vector_results):
                results.append(vector_results[doc_id])
            else:
                results.append(keyword_results[doc_id - len(vector_results)])

        return results

    def _keyword_search(self, query: str, k: int) -> List[SearchResult]:
        """简单的关键词搜索"""
        query_terms = set(query.lower().split())
        results = []

        for i, doc in enumerate(self.vector_store.documents):
            content = doc.content if hasattr(doc, 'content') else str(doc)
            content_terms = set(content.lower().split())

            # 计算关键词匹配度
            matches = len(query_terms.intersection(content_terms))
            if matches > 0:
                score = matches / len(query_terms)
                results.append(SearchResult(
                    document=doc,
                    score=score,
                    metadata=doc.metadata if hasattr(doc, 'metadata') else {},
                    source=doc.metadata.get('source', 'unknown') if hasattr(doc, 'metadata') else 'unknown'
                ))

        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:k]


# 使用示例
if __name__ == "__main__":
    from src.data_loaders import Document, load_documents

    # 1. 创建向量存储
    vector_store = InMemoryVectorStore()
    rag = RAGSystem(vector_store)

    # 2. 加载文档
    documents = load_documents('/path/to/docs', 'directory')
    print(f"加载了 {len(documents)} 个文档")

    # 3. 添加到 RAG 系统
    rag.add_documents(documents)

    # 4. 查询
    result = rag.query("如何实现文件操作？")
    print(f"问题: {result['question']}")
    print(f"答案: {result['answer'][:200]}...")
    print(f"置信度: {result['confidence']:.2f}")
    print(f"相关文档数: {len(result['relevant_documents'])}")

    # 5. 保存
    rag.save('rag_store.pkl')

    # 6. 加载
    rag.load('rag_store.pkl')
