#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络工具模块
"""

import os
import sys
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.memory_agent import BaseTool
from core import get_config_value


class HttpGetTool(BaseTool):
    """HTTP GET 请求工具"""

    def __init__(self):
        super().__init__(
            name="http_get",
            description="发送HTTP GET请求。参数: {\"url\": \"目标URL\"}"
        )
        self._load_config()

    def _load_config(self):
        # 从配置文件加载
        self.timeout = get_config_value("tools_config", "tools.network.timeout", 30)

    def execute(self, url: str, params: Dict = None) -> Dict[str, Any]:
        try:
            import requests
            response = requests.get(url, params=params, timeout=self.timeout)
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "content": response.text[:5000],  # 限制返回长度
                "headers": dict(response.headers)
            }
        except ImportError:
            return {"success": False, "error": "需要安装 requests 库: pip install requests"}
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}


class HttpPostTool(BaseTool):
    """HTTP POST 请求工具"""

    def __init__(self):
        super().__init__(
            name="http_post",
            description="发送HTTP POST请求。参数: {\"url\": \"URL\", \"data\": {数据}}"
        )
        self._load_config()

    def _load_config(self):
        # 从配置文件加载
        self.timeout = get_config_value("tools_config", "tools.network.timeout", 30)

    def execute(self, url: str, data: Dict = None, json_data: Dict = None) -> Dict[str, Any]:
        try:
            import requests
            if json_data:
                response = requests.post(url, json=json_data, timeout=self.timeout)
            else:
                response = requests.post(url, data=data, timeout=self.timeout)
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "content": response.text[:5000]
            }
        except ImportError:
            return {"success": False, "error": "需要安装 requests 库"}
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}


class WebSearchTool(BaseTool):
    """网络搜索工具 - 支持多搜索引擎"""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="网络搜索。参数: {\"query\": \"搜索词\", \"engine\": \"搜索引擎(duckduckgo/baidu/google/bing)\", \"num_results\": 结果数量}"
        )

    def _parse_duckduckgo(self, html: str, num_results: int) -> list:
        """解析 DuckDuckGo 搜索结果"""
        import re
        results = []

        # 提取标题和URL
        title_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.+?)</a>'
        matches = re.findall(title_pattern, html, re.DOTALL)

        # 提取摘要
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>(.+?)</a>'
        snippets = re.findall(snippet_pattern, html, re.DOTALL)

        for i, (url, title) in enumerate(matches[:num_results]):
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = ""
            if i < len(snippets):
                clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()

            results.append({
                "title": clean_title,
                "snippet": clean_snippet[:150],
                "url": url
            })
        return results

    def _parse_baidu(self, html: str, num_results: int) -> list:
        """解析百度搜索结果"""
        import re
        results = []

        # 百度结果模式 - 更灵活的匹配
        title_pattern = r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.+?)</a>.*?</h3>'
        matches = re.findall(title_pattern, html, re.DOTALL)

        for i, (url, title) in enumerate(matches[:num_results]):
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            results.append({
                "title": clean_title,
                "snippet": "",
                "url": url
            })
        return results

    def execute(self, query: str, engine: str = "duckduckgo", num_results: int = 5) -> Dict[str, Any]:
        """执行网络搜索

        Args:
            query: 搜索关键词
            engine: 搜索引擎 (duckduckgo/baidu/google/bing)
            num_results: 返回结果数量
        """
        try:
            import requests
            from urllib.parse import quote
            import time
            import random

            # 增强的请求头，模拟真实浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            engine = engine.lower()
            results = []

            if engine == "duckduckgo":
                url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = requests.get(url, headers=headers, timeout=10)
                results = self._parse_duckduckgo(response.text, num_results)

            elif engine == "baidu":
                # 百度反爬严重，添加延时和更多请求头
                time.sleep(random.uniform(1, 3))
                url = f"https://www.baidu.com/s?wd={quote(query)}&tn=json&制rn=5"
                response = requests.get(url, headers=headers, timeout=10)
                # 检查是否是安全验证页面
                if "安全验证" in response.text or "timeout" in response.text.lower():
                    # 降级到DuckDuckGo
                    engine = "duckduckgo"
                    url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                    response = requests.get(url, headers=headers, timeout=10)
                    results = self._parse_duckduckgo(response.text, num_results)
                else:
                    results = self._parse_baidu(response.text, num_results)

            elif engine == "google":
                # Google有反爬虫机制，降级到DuckDuckGo
                print(f"[WebSearch] Google搜索引擎受限，降级到DuckDuckGo")
                engine = "duckduckgo"
                url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = requests.get(url, headers=headers, timeout=10)
                results = self._parse_duckduckgo(response.text, num_results)

            elif engine == "bing":
                # Bing搜索API需要密钥，这里提供基础实现
                url = f"https://www.bing.com/search?q={quote(query)}"
                response = requests.get(url, headers=headers, timeout=10)
                results = [{"title": "Bing搜索", "snippet": f"搜索词: {query}", "url": url}]

            else:
                return {
                    "success": False,
                    "query": query,
                    "engine": engine,
                    "error": f"不支持的搜索引擎: {engine}。支持: duckduckgo, baidu, google, bing"
                }

            if results:
                return {
                    "success": True,
                    "query": query,
                    "engine": engine,
                    "results": results,
                    "count": len(results)
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "engine": engine,
                    "error": "未找到搜索结果"
                }

        except requests.exceptions.Timeout:
            return {"success": False, "query": query, "engine": engine, "error": "搜索超时"}
        except Exception as e:
            return {"success": False, "query": query, "engine": engine, "error": str(e)}


class DownloadTool(BaseTool):
    """文件下载工具"""

    def __init__(self):
        super().__init__(
            name="download",
            description="下载文件。参数: {\"url\": \"URL\", \"filepath\": \"保存路径\"}"
        )
        self._load_config()

    def _load_config(self):
        try:
            # 使用硬编码配置
            # config = get_config("tools_config", "tools.network", {})
            self.max_size = config.get("max_download_size", 100 * 1024 * 1024)
            self.timeout = config.get("timeout", 60)
        except:
            self.max_size = 100 * 1024 * 1024
            self.timeout = 60

    def execute(self, url: str, filepath: str) -> Dict[str, Any]:
        try:
            import requests

            # 先获取文件大小
            head = requests.head(url, timeout=10)
            size = int(head.headers.get('content-length', 0))

            if size > self.max_size:
                return {
                    "success": False,
                    "error": f"文件过大: {size} 字节 (最大 {self.max_size})"
                }

            # 下载
            response = requests.get(url, stream=True, timeout=self.timeout)

            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)) or '.', exist_ok=True)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return {
                "success": True,
                "url": url,
                "filepath": os.path.abspath(filepath),
                "size": os.path.getsize(filepath)
            }
        except ImportError:
            return {"success": False, "error": "需要安装 requests 库"}
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}
