#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件读取模块
"""

import os
from typing import Dict, Any, Optional


class FileReader:
    """文件读取器"""

    def __init__(self, max_size: int = 10 * 1024 * 1024):
        self.max_size = max_size  # 默认最大 10MB

    def read(self, filepath: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """读取文件内容"""
        try:
            abs_path = os.path.abspath(filepath)

            if not os.path.exists(abs_path):
                return {"success": False, "error": f"文件不存在: {filepath}"}

            if not os.path.isfile(abs_path):
                return {"success": False, "error": f"不是文件: {filepath}"}

            size = os.path.getsize(abs_path)
            if size > self.max_size:
                return {"success": False, "error": f"文件过大: {size} 字节"}

            with open(abs_path, 'r', encoding=encoding) as f:
                content = f.read()

            return {
                "success": True,
                "filepath": abs_path,
                "content": content,
                "size": size,
                "lines": content.count('\n') + 1
            }
        except UnicodeDecodeError:
            return {"success": False, "error": "文件编码错误，尝试其他编码"}
        except Exception as e:
            return {"success": False, "filepath": filepath, "error": str(e)}

    def read_lines(self, filepath: str, start: int = 0, count: int = None,
                   encoding: str = "utf-8") -> Dict[str, Any]:
        """按行读取文件"""
        try:
            abs_path = os.path.abspath(filepath)

            if not os.path.exists(abs_path):
                return {"success": False, "error": f"文件不存在: {filepath}"}

            with open(abs_path, 'r', encoding=encoding) as f:
                lines = f.readlines()

            if count:
                lines = lines[start:start + count]
            else:
                lines = lines[start:]

            return {
                "success": True,
                "filepath": abs_path,
                "lines": lines,
                "count": len(lines),
                "start": start
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_binary(self, filepath: str) -> Dict[str, Any]:
        """读取二进制文件"""
        try:
            abs_path = os.path.abspath(filepath)

            if not os.path.exists(abs_path):
                return {"success": False, "error": f"文件不存在: {filepath}"}

            size = os.path.getsize(abs_path)
            if size > self.max_size:
                return {"success": False, "error": f"文件过大: {size} 字节"}

            with open(abs_path, 'rb') as f:
                content = f.read()

            return {
                "success": True,
                "filepath": abs_path,
                "content": content,
                "size": size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
