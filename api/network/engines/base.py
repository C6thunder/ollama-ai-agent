#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索引擎基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseSearchEngine(ABC):
    """搜索引擎基类"""

    def __init__(self, name: str, timeout: int = 10):
        self.name = name
        self.timeout = timeout

    @abstractmethod
    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果
        """
        pass

    def _clean_html(self, text: str) -> str:
        """清理 HTML 标签"""
        import re
        return re.sub(r'<[^>]+>', '', text).strip()

    def _build_result(self, success: bool, query: str, results: List = None,
                      error: str = None, note: str = None) -> Dict[str, Any]:
        """构建统一的返回结果"""
        result = {
            "success": success,
            "query": query,
            "engine": self.name
        }
        if success:
            result["results"] = results or []
            result["count"] = len(result["results"])
        else:
            result["error"] = error
        if note:
            result["note"] = note
        return result
