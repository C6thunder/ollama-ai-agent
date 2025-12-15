#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuckDuckGo 搜索引擎
"""

import re
import requests
from urllib.parse import quote
from typing import Dict, Any
from .base import BaseSearchEngine


class DuckDuckGoEngine(BaseSearchEngine):
    """DuckDuckGo 搜索引擎"""

    def __init__(self, timeout: int = 10):
        super().__init__("duckduckgo", timeout)
        self.html_url = "https://html.duckduckgo.com/html/"
        self.api_url = "https://api.duckduckgo.com/"

    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """使用 DuckDuckGo HTML 版本搜索"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            url = f"{self.html_url}?q={quote(query)}"
            response = requests.get(url, headers=headers, timeout=self.timeout)
            html = response.text

            results = self._parse_html_results(html, num_results)

            if results:
                return self._build_result(True, query, results)
            else:
                return self._build_result(False, query, error="未找到搜索结果")

        except requests.Timeout:
            return self._build_result(False, query, error="搜索超时")
        except Exception as e:
            return self._build_result(False, query, error=str(e))

    def _parse_html_results(self, html: str, num_results: int) -> list:
        """解析 HTML 搜索结果"""
        results = []

        # 提取标题和URL
        title_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.+?)</a>'
        matches = re.findall(title_pattern, html, re.DOTALL)

        # 提取摘要
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>(.+?)</a>'
        snippets = re.findall(snippet_pattern, html, re.DOTALL)

        for i, (url, title) in enumerate(matches[:num_results]):
            clean_title = self._clean_html(title)
            clean_snippet = ""
            if i < len(snippets):
                clean_snippet = self._clean_html(snippets[i])[:150]

            results.append({
                "title": clean_title,
                "snippet": clean_snippet,
                "url": url,
                "source": "DuckDuckGo"
            })

        return results

    def search_api(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """使用 DuckDuckGo API 搜索（即时答案）"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }

            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            data = response.json()

            results = []

            # 提取即时答案
            if data.get('Abstract'):
                results.append({
                    "title": data.get('Heading', 'Instant Answer'),
                    "snippet": data['Abstract'],
                    "url": data.get('AbstractURL', ''),
                    "source": "DuckDuckGo"
                })

            # 提取相关主题
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if 'Text' in topic and topic.get('FirstURL'):
                    results.append({
                        "title": topic.get('Text', '').split(' - ')[0],
                        "snippet": topic['Text'],
                        "url": topic.get('FirstURL', ''),
                        "source": "DuckDuckGo"
                    })

            return self._build_result(True, query, results)

        except Exception as e:
            return self._build_result(False, query, error=str(e))
