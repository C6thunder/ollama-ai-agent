#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络 API 模块
"""

from .http import HttpClient
from .download import Downloader
from .search import SearchAPI
from .scraper import WebScraper
from .engines import (
    BaseSearchEngine,
    DuckDuckGoEngine,
    BaiduEngine,
    GoogleEngine,
    BingEngine
)


class NetworkAPI:
    """
    网络 API 统一入口
    兼容原有接口
    """

    def __init__(self, timeout: int = 30):
        self.http = HttpClient(timeout)
        self.downloader = Downloader(timeout)
        self.search_api = SearchAPI(timeout=timeout)
        self.scraper = WebScraper(timeout)

    def get(self, url: str, params=None, headers=None):
        """HTTP GET 请求"""
        return self.http.get(url, params, headers)

    def post(self, url: str, data=None, json_data=None, headers=None):
        """HTTP POST 请求"""
        return self.http.post(url, data, json_data, headers)

    def download(self, url: str, filepath: str):
        """下载文件"""
        return self.downloader.download(url, filepath)

    def search(self, query: str, engine: str = "duckduckgo", num_results: int = 5):
        """网络搜索"""
        return self.search_api.search(query, engine, num_results)

    def scrape(self, url: str):
        """抓取网页"""
        return self.scraper.scrape(url)


__all__ = [
    'NetworkAPI',
    'HttpClient',
    'Downloader',
    'SearchAPI',
    'WebScraper',
    'BaseSearchEngine',
    'DuckDuckGoEngine',
    'BaiduEngine',
    'GoogleEngine',
    'BingEngine'
]
