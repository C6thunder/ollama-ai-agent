#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件写入模块
"""

import os
import json
from typing import Dict, Any, Optional, List


class FileWriter:
    """文件写入器"""

    # 受保护的路径
    PROTECTED_PATHS = ["/etc", "/usr", "/bin", "/sbin", "/boot", "/root", "/sys", "/proc", "/dev"]

    def __init__(self, protected_paths: List[str] = None):
        self.protected_paths = protected_paths or self.PROTECTED_PATHS

    def _is_path_safe(self, filepath: str) -> tuple:
        """检查路径是否安全"""
        abs_path = os.path.abspath(filepath)
        for protected in self.protected_paths:
            if abs_path.startswith(protected):
                return False, f"无法写入受保护路径: {protected}"
        return True, "OK"

    def write(self, filepath: str, content: str,
              encoding: str = "utf-8") -> Dict[str, Any]:
        """写入文件"""
        try:
            abs_path = os.path.abspath(filepath)

            # 安全检查
            is_safe, msg = self._is_path_safe(abs_path)
            if not is_safe:
                return {"success": False, "error": msg}

            # 创建目录
            dir_path = os.path.dirname(abs_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            with open(abs_path, 'w', encoding=encoding) as f:
                f.write(content)

            return {
                "success": True,
                "filepath": abs_path,
                "size": len(content),
                "message": f"文件已写入: {abs_path}"
            }
        except Exception as e:
            return {"success": False, "filepath": filepath, "error": str(e)}

    def append(self, filepath: str, content: str,
               encoding: str = "utf-8") -> Dict[str, Any]:
        """追加写入文件"""
        try:
            abs_path = os.path.abspath(filepath)

            is_safe, msg = self._is_path_safe(abs_path)
            if not is_safe:
                return {"success": False, "error": msg}

            dir_path = os.path.dirname(abs_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            with open(abs_path, 'a', encoding=encoding) as f:
                f.write(content)

            return {
                "success": True,
                "filepath": abs_path,
                "appended": len(content),
                "message": f"内容已追加: {abs_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_json(self, filepath: str, data: Any,
                   indent: int = 2) -> Dict[str, Any]:
        """写入 JSON 文件"""
        try:
            content = json.dumps(data, ensure_ascii=False, indent=indent)
            return self.write(filepath, content)
        except Exception as e:
            return {"success": False, "error": f"JSON 序列化错误: {e}"}

    def write_lines(self, filepath: str, lines: List[str],
                    encoding: str = "utf-8") -> Dict[str, Any]:
        """按行写入文件"""
        content = '\n'.join(lines)
        return self.write(filepath, content, encoding)
