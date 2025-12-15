#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell API 模块
"""

from .executor import ShellExecutor

# 别名，兼容原有代码
ShellAPI = ShellExecutor

__all__ = ['ShellExecutor', 'ShellAPI']
