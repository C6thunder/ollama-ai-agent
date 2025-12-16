"""数据加载器模块

支持多种数据源的加载，包括：
- 文本文件 (TXT, MD, PY, JSON, YAML)
- 网页内容 (HTML)
- 目录批量加载
- 数据库连接
- API 数据获取

所有加载器都返回统一的文档格式
"""

import os
import json
import yaml
import re
from typing import List, Dict, Any, Optional, Union, Iterator
from abc import ABC, abstractmethod
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Document:
    """文档类"""

    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        doc_type: Optional[str] = None
    ):
        self.content = content
        self.metadata = metadata or {}
        self.source = source or "unknown"
        self.doc_type = doc_type or "text"
        self.page_content = content  # 兼容性

    def __repr__(self):
        return f"Document(source={self.source}, type={self.doc_type}, length={len(self.content)})"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "source": self.source,
            "doc_type": self.doc_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """从字典创建"""
        return cls(
            content=data["content"],
            metadata=data.get("metadata", {}),
            source=data.get("source", "unknown"),
            doc_type=data.get("doc_type", "text")
        )


class BaseDataLoader(ABC):
    """数据加载器基类"""

    @abstractmethod
    def load(self, source: str) -> List[Document]:
        """加载数据"""
        pass

    def load_and_split(
        self,
        source: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Document]:
        """加载数据并分块"""
        documents = self.load(source)
        return self._split_documents(documents, chunk_size, chunk_overlap)

    def _split_documents(
        self,
        documents: List[Document],
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Document]:
        """拆分文档"""
        chunks = []
        for doc in documents:
            if len(doc.content) <= chunk_size:
                chunks.append(doc)
            else:
                # 简单分块逻辑（实际可使用更复杂的算法）
                start = 0
                while start < len(doc.content):
                    end = start + chunk_size
                    chunk_content = doc.content[start:end]

                    chunk_metadata = doc.metadata.copy()
                    chunk_metadata["chunk_index"] = start // chunk_size

                    chunks.append(Document(
                        content=chunk_content,
                        metadata=chunk_metadata,
                        source=doc.source,
                        doc_type=doc.doc_type
                    ))

                    start += chunk_size - chunk_overlap

        return chunks


class TextFileLoader(BaseDataLoader):
    """文本文件加载器"""

    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.py', '.js', '.java', '.cpp', '.c', '.h',
        '.json', '.yaml', '.yml', '.xml', '.csv', '.log',
        '.html', '.css', '.sh', '.sql', '.rst'
    }

    def __init__(
        self,
        encoding: str = 'utf-8',
        metadata_extractors: Optional[Dict[str, callable]] = None
    ):
        self.encoding = encoding
        self.metadata_extractors = metadata_extractors or {}

    def load(self, source: str) -> List[Document]:
        """加载文本文件"""
        try:
            # 检查文件是否存在
            if not os.path.exists(source):
                raise FileNotFoundError(f"文件不存在: {source}")

            # 检查扩展名
            ext = Path(source).suffix.lower()
            if ext not in self.SUPPORTED_EXTENSIONS:
                logger.warning(f"不支持的文件类型: {ext}")

            # 读取文件
            with open(source, 'r', encoding=self.encoding) as f:
                content = f.read()

            # 提取元数据
            metadata = self._extract_metadata(source, content)

            return [Document(
                content=content,
                metadata=metadata,
                source=source,
                doc_type=ext[1:] if ext else "text"
            )]

        except Exception as e:
            logger.error(f"加载文件失败 {source}: {str(e)}")
            raise

    def _extract_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """提取文件元数据"""
        metadata = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "extension": Path(file_path).suffix.lower()
        }

        # 应用元数据提取器
        for extractor_name, extractor_func in self.metadata_extractors.items():
            try:
                metadata[extractor_name] = extractor_func(file_path, content)
            except Exception as e:
                logger.warning(f"元数据提取器 '{extractor_name}' 失败: {str(e)}")

        return metadata


class DirectoryLoader(BaseDataLoader):
    """目录加载器"""

    def __init__(
        self,
        extensions: Optional[List[str]] = None,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None
    ):
        self.extensions = extensions or ['.txt', '.md', '.py', '.json', '.yaml', '.yml']
        self.recursive = recursive
        self.exclude_patterns = exclude_patterns or [
            '__pycache__', '.git', '.pytest_cache', 'node_modules',
            'venv', 'env', '.env', '*.pyc', '*.pyo'
        ]

    def load(self, source: str) -> List[Document]:
        """加载目录中的所有文件"""
        if not os.path.exists(source) or not os.path.isdir(source):
            raise ValueError(f"目录不存在: {source}")

        documents = []
        file_loader = TextFileLoader()

        for root, dirs, files in os.walk(source):
            # 过滤目录
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]

            for file in files:
                if self._should_exclude(file):
                    continue

                file_path = os.path.join(root, file)
                ext = Path(file).suffix.lower()

                # 检查扩展名
                if ext not in self.extensions:
                    continue

                try:
                    docs = file_loader.load(file_path)
                    documents.extend(docs)
                except Exception as e:
                    logger.warning(f"加载文件失败 {file_path}: {str(e)}")

        logger.info(f"从目录 {source} 加载了 {len(documents)} 个文档")
        return documents

    def _should_exclude(self, name: str) -> bool:
        """判断是否应该排除"""
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern in name:
                return True
        return False


class JSONLoader(BaseDataLoader):
    """JSON 文件加载器"""

    def __init__(
        self,
        text_fields: Optional[List[str]] = None,
        metadata_fields: Optional[List[str]] = None
    ):
        self.text_fields = text_fields or ["content", "text", "description"]
        self.metadata_fields = metadata_fields or ["title", "author", "date"]

    def load(self, source: str) -> List[Document]:
        """加载 JSON 文件"""
        try:
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)

            documents = []
            if isinstance(data, list):
                for item in data:
                    doc = self._create_document_from_item(item, source)
                    if doc:
                        documents.append(doc)
            elif isinstance(data, dict):
                doc = self._create_document_from_item(data, source)
                if doc:
                    documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"加载 JSON 文件失败 {source}: {str(e)}")
            raise

    def _create_document_from_item(
        self,
        item: Dict[str, Any],
        source: str
    ) -> Optional[Document]:
        """从 JSON 项创建文档"""
        # 提取文本内容
        content = ""
        for field in self.text_fields:
            if field in item:
                content += str(item[field]) + "\n"

        if not content.strip():
            return None

        # 提取元数据
        metadata = {}
        for field in self.metadata_fields:
            if field in item:
                metadata[field] = item[field]

        metadata["source"] = source

        return Document(
            content=content.strip(),
            metadata=metadata,
            source=source,
            doc_type="json"
        )


class YAMLLoader(BaseDataLoader):
    """YAML 文件加载器"""

    def load(self, source: str) -> List[Document]:
        """加载 YAML 文件"""
        try:
            with open(source, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # 转换为 JSON 格式处理
            json_loader = JSONLoader()
            return json_loader._create_document_from_item(data, source)

        except Exception as e:
            logger.error(f"加载 YAML 文件失败 {source}: {str(e)}")
            raise


class MarkdownLoader(BaseDataLoader):
    """Markdown 文件专用加载器"""

    def load(self, source: str) -> List[Document]:
        """加载 Markdown 文件"""
        try:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析 Markdown 元数据（如果存在）
            metadata = self._extract_markdown_metadata(content)

            # 移除元数据头部
            content = self._remove_metadata_header(content)

            # 提取标题
            title = self._extract_title(content)

            metadata.update({
                "title": title,
                "source": source,
                "file_size": os.path.getsize(source)
            })

            return [Document(
                content=content,
                metadata=metadata,
                source=source,
                doc_type="markdown"
            )]

        except Exception as e:
            logger.error(f"加载 Markdown 文件失败 {source}: {str(e)}")
            raise

    def _extract_markdown_metadata(self, content: str) -> Dict[str, Any]:
        """提取 Markdown 元数据"""
        metadata = {}

        # 检查是否使用 YAML frontmatter
        if content.startswith('---'):
            try:
                end = content.find('---', 3)
                if end != -1:
                    frontmatter = content[3:end].strip()
                    metadata.update(yaml.safe_load(frontmatter))
            except Exception as e:
                logger.warning(f"解析 frontmatter 失败: {str(e)}")

        return metadata

    def _remove_metadata_header(self, content: str) -> str:
        """移除元数据头部"""
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                return content[end+3:].strip()
        return content

    def _extract_title(self, content: str) -> str:
        """提取文档标题"""
        # 查找第一个 # 标题
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                return line.lstrip('#').strip()
        return "无标题"


class CSVLoader(BaseDataLoader):
    """CSV 文件加载器"""

    def __init__(
        self,
        text_columns: Optional[List[str]] = None,
        metadata_columns: Optional[List[str]] = None,
        delimiter: str = ','
    ):
        self.text_columns = text_columns or []
        self.metadata_columns = metadata_columns or []
        self.delimiter = delimiter

    def load(self, source: str) -> List[Document]:
        """加载 CSV 文件"""
        try:
            import csv

            documents = []
            with open(source, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)

                for row in reader:
                    # 提取文本内容
                    content_parts = []
                    if self.text_columns:
                        for col in self.text_columns:
                            if col in row and row[col]:
                                content_parts.append(f"{col}: {row[col]}")
                    else:
                        # 使用所有列
                        content_parts = [f"{k}: {v}" for k, v in row.items() if v]

                    content = "\n".join(content_parts)

                    # 提取元数据
                    metadata = {}
                    for col in self.metadata_columns:
                        if col in row:
                            metadata[col] = row[col]

                    metadata["source"] = source

                    documents.append(Document(
                        content=content,
                        metadata=metadata,
                        source=source,
                        doc_type="csv"
                    ))

            return documents

        except Exception as e:
            logger.error(f"加载 CSV 文件失败 {source}: {str(e)}")
            raise


class DataLoaderManager:
    """数据加载器管理器"""

    LOADERS = {
        'text': TextFileLoader,
        'directory': DirectoryLoader,
        'json': JSONLoader,
        'yaml': YAMLLoader,
        'markdown': MarkdownLoader,
        'csv': CSVLoader
    }

    def __init__(self):
        self._loader_instances = {}

    def get_loader(self, loader_type: str, **kwargs) -> BaseDataLoader:
        """获取加载器实例"""
        if loader_type not in self.LOADERS:
            raise ValueError(f"不支持的加载器类型: {loader_type}")

        if loader_type not in self._loader_instances:
            loader_class = self.LOADERS[loader_type]
            self._loader_instances[loader_type] = loader_class(**kwargs)

        return self._loader_instances[loader_type]

    def load_data(
        self,
        source: str,
        loader_type: Optional[str] = None,
        **kwargs
    ) -> List[Document]:
        """加载数据

        Args:
            source: 数据源路径
            loader_type: 加载器类型（自动检测如果未提供）
            **kwargs: 加载器参数

        Returns:
            文档列表
        """
        # 自动检测加载器类型
        if loader_type is None:
            loader_type = self._detect_loader_type(source)

        loader = self.get_loader(loader_type, **kwargs)
        return loader.load(source)

    def _detect_loader_type(self, source: str) -> str:
        """自动检测加载器类型"""
        if os.path.isdir(source):
            return 'directory'

        ext = Path(source).suffix.lower()
        ext_to_loader = {
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.csv': 'csv',
            '.md': 'markdown',
            '.txt': 'text'
        }

        return ext_to_loader.get(ext, 'text')

    def list_supported_types(self) -> List[str]:
        """列出支持的加载器类型"""
        return list(self.LOADERS.keys())

    def load_and_split(
        self,
        source: str,
        loader_type: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs
    ) -> List[Document]:
        """加载数据并分块"""
        loader = self.get_loader(loader_type or self._detect_loader_type(source), **kwargs)
        return loader.load_and_split(source, chunk_size, chunk_overlap)


# 全局数据加载器管理器实例
data_loader_manager = DataLoaderManager()


def get_data_loader(loader_type: str, **kwargs) -> BaseDataLoader:
    """获取数据加载器"""
    return data_loader_manager.get_loader(loader_type, **kwargs)


def load_documents(
    source: str,
    loader_type: Optional[str] = None,
    **kwargs
) -> List[Document]:
    """便捷函数：加载文档"""
    return data_loader_manager.load_data(source, loader_type, **kwargs)


# 使用示例
if __name__ == "__main__":
    # 1. 加载单个文件
    loader = get_data_loader('text')
    docs = loader.load('example.txt')
    print(f"加载了 {len(docs)} 个文档")

    # 2. 加载目录
    docs = load_documents('/path/to/docs', 'directory')
    print(f"从目录加载了 {len(docs)} 个文档")

    # 3. 加载 JSON 文件
    docs = load_documents('data.json', 'json')
    print(f"从 JSON 加载了 {len(docs)} 个文档")

    # 4. 自动检测类型
    docs = load_documents('README.md')  # 自动检测为 markdown
    print(f"自动检测加载了 {len(docs)} 个文档")

    # 5. 加载并分块
    docs = data_loader_manager.load_and_split(
        'large_document.txt',
        chunk_size=500,
        chunk_overlap=50
    )
    print(f"分块后得到 {len(docs)} 个文档块")
