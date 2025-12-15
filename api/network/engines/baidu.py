#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度搜索引擎
"""

import re
import requests
from urllib.parse import quote
from typing import Dict, Any
from .base import BaseSearchEngine


class BaiduEngine(BaseSearchEngine):
    """百度搜索引擎"""

    def __init__(self, timeout: int = 10):
        super().__init__("baidu", timeout)
        self.search_url = "https://www.baidu.com/s"

    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """使用百度搜索"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }

            params = {'wd': query}
            response = requests.get(
                self.search_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            html = response.text

            # 检查是否被验证
            if "安全验证" in html or "网络不给力" in html:
                return self._build_result(
                    False, query,
                    error="百度安全验证",
                    note="建议使用其他搜索引擎"
                )

            results = self._parse_results(html, num_results)

            if results:
                return self._build_result(True, query, results)
            else:
                return self._build_result(
                    False, query,
                    error="未找到搜索结果",
                    note="百度反爬虫机制可能阻止了访问"
                )

        except requests.Timeout:
            return self._build_result(False, query, error="搜索超时")
        except Exception as e:
            return self._build_result(False, query, error=str(e))

    def _parse_results(self, html: str, num_results: int) -> list:
        """解析百度搜索结果"""
        results = []

        # 多种匹配模式
        patterns = [
            r'<h3[^>]*class="[^"]*t[^"]*"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>',
            r'<div[^>]*class="[^"]*result[^"]*"[^>]*>.*?<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            if matches:
                for href, title in matches[:num_results]:
                    clean_title = self._clean_html(title)
                    if clean_title:
                        results.append({
                            "title": clean_title,
                            "snippet": "",
                            "url": href,
                            "source": "Baidu"
                        })
                break

        return results
