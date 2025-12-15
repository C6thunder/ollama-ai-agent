#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像 API 模块
"""

from .processor import ImageProcessor

# 别名，兼容原有代码
ImageAPI = ImageProcessor

__all__ = ['ImageProcessor', 'ImageAPI']
