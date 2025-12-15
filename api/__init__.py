#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 模块主入口
统一导出所有 API
"""

# 从新的模块化结构导入
from .network import NetworkAPI, SearchAPI, HttpClient, Downloader, WebScraper
from .network.engines import DuckDuckGoEngine, BaiduEngine, GoogleEngine, BingEngine
from .file import FileAPI, FileReader, FileWriter, FileOperations
from .llm import OllamaAPI, OllamaClient
from .shell import ShellAPI, ShellExecutor
from .data import DataAPI, DataAnalyzer
from .image import ImageAPI, ImageProcessor

__all__ = [
    # Network
    'NetworkAPI',
    'SearchAPI',
    'HttpClient',
    'Downloader',
    'WebScraper',
    'DuckDuckGoEngine',
    'BaiduEngine',
    'GoogleEngine',
    'BingEngine',

    # File
    'FileAPI',
    'FileReader',
    'FileWriter',
    'FileOperations',

    # LLM
    'OllamaAPI',
    'OllamaClient',

    # Shell
    'ShellAPI',
    'ShellExecutor',

    # Data
    'DataAPI',
    'DataAnalyzer',

    # Image
    'ImageAPI',
    'ImageProcessor'
]
