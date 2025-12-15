#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页抓取模块
"""

import re
import requests
from typing import Dict, Any, List, Optional


class WebScraper:
    """网页抓取器"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape(self, url: str) -> Dict[str, Any]:
        """
        抓取网页内容

        Args:
            url: 网页 URL

        Returns:
            网页内容
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            html = response.text

            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "title": self._extract_title(html),
                "text": self._extract_text(html),
                "links": self._extract_links(html),
                "images": self._extract_images(html)
            }
        except requests.Timeout:
            return {"success": False, "url": url, "error": "请求超时"}
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}

    def _extract_title(self, html: str) -> str:
        """提取标题"""
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_text(self, html: str, max_length: int = 5000) -> str:
        """提取正文文本"""
        # 移除脚本和样式
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # 移除所有标签
        text = re.sub(r'<[^>]+>', ' ', html)
        # 清理空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_length]

    def _extract_links(self, html: str, max_count: int = 50) -> List[str]:
        """提取链接"""
        pattern = r'<a[^>]*href=["\'](https?://[^"\']+)["\']'
        links = re.findall(pattern, html, re.IGNORECASE)
        return list(set(links))[:max_count]

    def _extract_images(self, html: str, max_count: int = 20) -> List[str]:
        """提取图片链接"""
        pattern = r'<img[^>]*src=["\'](https?://[^"\']+)["\']'
        images = re.findall(pattern, html, re.IGNORECASE)
        return list(set(images))[:max_count]
