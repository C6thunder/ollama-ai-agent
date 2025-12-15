#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM API 模块
"""

from .ollama import OllamaClient
from .langchain_ollama import LangChainOllamaLLM, OllamaLLM

# 别名，兼容原有代码
OllamaAPI = OllamaClient

__all__ = ['OllamaClient', 'OllamaAPI', 'LangChainOllamaLLM', 'OllamaLLM']
