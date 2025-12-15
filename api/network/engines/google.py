#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google 搜索引擎
"""

import re
import requests
from urllib.parse import quote
from typing import Dict, Any
from .base import BaseSearchEngine


class GoogleEngine(BaseSearchEngine):
    """Google 搜索引擎"""

    def __init__(self, timeout: int = 10):
        super().__init__("google", timeout)
        self.search_url = "https://www.google.com/search"

    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """使用 Google 搜索（可能需要代理）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            params = {'q': query, 'num': num_results * 2}
            response = requests.get(
                self.search_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            html = response.text

            # 检查是否需要验证
            if "enablejs" in html or "captcha" in html.lower():
                return self._build_result(
                    False, query,
                    error="Google 需要验证",
                    note="建议使用 DuckDuckGo"
                )

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
        """解析 Google 搜索结果"""
        results = []

        patterns = [
            r'<div[^>]*class="[^"]*g[^"]*"[^>]*>.*?<h3[^>]*>(.*?)</h3>.*?<a[^>]*href="([^"]*)"',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            if matches:
                for title, href in matches[:num_results]:
                    clean_title = self._clean_html(title)
                    if clean_title and href.startswith('http'):
                        results.append({
                            "title": clean_title,
                            "snippet": "",
                            "url": href,
                            "source": "Google"
                        })
                break

        return results
