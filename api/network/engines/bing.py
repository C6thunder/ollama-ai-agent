#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bing 搜索引擎
"""

import re
import requests
from urllib.parse import quote
from typing import Dict, Any
from .base import BaseSearchEngine


class BingEngine(BaseSearchEngine):
    """Bing 搜索引擎"""

    def __init__(self, timeout: int = 10):
        super().__init__("bing", timeout)
        self.search_url = "https://www.bing.com/search"

    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """使用 Bing 搜索"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }

            params = {'q': query}
            response = requests.get(
                self.search_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            html = response.text

            results = self._parse_results(html, num_results)

            if results:
                return self._build_result(True, query, results)
            else:
                return self._build_result(False, query, error="未找到搜索结果")

        except requests.Timeout:
            return self._build_result(False, query, error="搜索超时")
        except Exception as e:
            return self._build_result(False, query, error=str(e))

    def _parse_results(self, html: str, num_results: int) -> list:
        """解析 Bing 搜索结果"""
        results = []

        # Bing 结果在 <li class="b_algo">
        pattern = r'<li class="b_algo">.*?<h2>.*?<a[^>]*href="([^"]*)"[^>]*>(.+?)</a>.*?</h2>.*?(?:<p[^>]*>(.+?)</p>)?'
        matches = re.findall(pattern, html, re.DOTALL)

        for url, title, snippet in matches[:num_results]:
            clean_title = self._clean_html(title)
            clean_snippet = self._clean_html(snippet) if snippet else ""

            if clean_title:
                results.append({
                    "title": clean_title,
                    "snippet": clean_snippet[:150],
                    "url": url,
                    "source": "Bing"
                })

        return results
