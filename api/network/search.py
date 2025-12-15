#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索 API 模块
统一的搜索接口
"""

from typing import Dict, Any, Optional
from .engines import DuckDuckGoEngine, BaiduEngine, GoogleEngine, BingEngine


class SearchAPI:
    """统一搜索 API"""

    def __init__(self, default_engine: str = "duckduckgo", timeout: int = 10):
        self.default_engine = default_engine
        self.timeout = timeout

        # 初始化所有搜索引擎
        self.engines = {
            "duckduckgo": DuckDuckGoEngine(timeout),
            "baidu": BaiduEngine(timeout),
            "google": GoogleEngine(timeout),
            "bing": BingEngine(timeout)
        }

    def search(self, query: str, engine: str = None,
               num_results: int = 5) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索关键词
            engine: 搜索引擎名称
            num_results: 返回结果数量

        Returns:
            搜索结果
        """
        engine_name = engine or self.default_engine

        if engine_name == "mixed":
            return self._mixed_search(query, num_results)

        if engine_name not in self.engines:
            return {
                "success": False,
                "error": f"不支持的搜索引擎: {engine_name}",
                "available_engines": list(self.engines.keys())
            }

        return self.engines[engine_name].search(query, num_results)

    def _mixed_search(self, query: str, num_results: int) -> Dict[str, Any]:
        """混合搜索：使用多个引擎并聚合结果"""
        all_results = []
        engine_status = {}

        for name, engine in self.engines.items():
            try:
                result = engine.search(query, num_results // len(self.engines) + 1)
                engine_status[name] = result.get("success", False)

                if result.get("success"):
                    all_results.extend(result.get("results", []))
            except Exception as e:
                engine_status[name] = False

        # 去重
        seen_urls = set()
        unique_results = []
        for r in all_results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)

        return {
            "success": bool(unique_results),
            "query": query,
            "engine": "mixed",
            "results": unique_results[:num_results],
            "count": len(unique_results[:num_results]),
            "engine_status": engine_status
        }

    def get_available_engines(self) -> list:
        """获取可用的搜索引擎列表"""
        return list(self.engines.keys()) + ["mixed"]
