#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据 API 模块
"""

from .analyzer import DataAnalyzer

# 别名，兼容原有代码
DataAPI = DataAnalyzer

__all__ = ['DataAnalyzer', 'DataAPI']
