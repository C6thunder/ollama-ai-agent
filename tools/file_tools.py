#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件操作工具模块
"""

import os
import shutil
from typing import Dict, Any, Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.memory_agent import BaseTool
from core import get_config_value


class FileReadTool(BaseTool):
    """文件读取工具"""

    def __init__(self):
        super().__init__(
            name="file_read",
            description="读取文件内容。参数: {\"filepath\": \"文件路径\"}"
        )
        self._load_config()

    def _load_config(self):
        # 从配置文件加载
        self.max_size = get_config_value("tools_config", "tools.file.max_file_size", 10 * 1024 * 1024)
        self.protected_paths = get_config_value("tools_config", "tools.file.protected_paths",
                                                ["/etc", "/usr", "/bin", "/sbin", "/boot", "/root"])

    def _is_path_safe(self, filepath: str) -> tuple:
        """检查路径安全性"""
        abs_path = os.path.abspath(filepath)

        # 获取当前用户主目录
        current_user_home = os.path.expanduser("~")

        # 允许访问用户主目录及其子目录
        if abs_path.startswith(current_user_home):
            return True, "OK"

        # 检查是否在保护路径内
        for protected in self.protected_paths:
            if abs_path.startswith(protected):
                return False, f"路径受保护: {protected}"

        return True, "OK"

    def execute(self, filepath: str, encoding: str = "utf-8") -> Dict[str, Any]:
        try:
            abs_path = os.path.abspath(filepath)

            if not os.path.exists(abs_path):
                return {"success": False, "error": f"文件不存在: {filepath}"}

            if os.path.getsize(abs_path) > self.max_size:
                return {"success": False, "error": f"文件过大 (最大 {self.max_size} 字节)"}

            with open(abs_path, 'r', encoding=encoding) as f:
                content = f.read()

            return {
                "success": True,
                "filepath": abs_path,
                "content": content,
                "size": len(content),
                "lines": content.count('\n') + 1
            }
        except Exception as e:
            return {"success": False, "filepath": filepath, "error": str(e)}


class FileWriteTool(BaseTool):
    """文件写入工具"""

    def __init__(self):
        super().__init__(
            name="file_write",
            description="写入文件内容。参数: {\"filepath\": \"路径\", \"content\": \"内容\"}"
        )
        self._load_config()

    def _load_config(self):
        # 从配置文件加载
        self.protected_paths = get_config_value("tools_config", "tools.file.protected_paths",
                                                ["/etc", "/usr", "/bin", "/sbin", "/boot", "/root"])
        self.allowed_extensions = get_config_value("tools_config", "tools.file.allowed_extensions", [])

    def _is_path_safe(self, filepath: str) -> tuple:
        """检查路径安全性"""
        abs_path = os.path.abspath(filepath)

        # 获取当前用户主目录
        current_user_home = os.path.expanduser("~")

        # 允许访问用户主目录及其子目录
        if abs_path.startswith(current_user_home):
            return True, "OK"

        # 检查是否在保护路径内
        for protected in self.protected_paths:
            if abs_path.startswith(protected):
                return False, f"路径受保护: {protected}"

        return True, "OK"

    def execute(self, filepath: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        try:
            abs_path = os.path.abspath(filepath)

            # 安全检查
            is_safe, msg = self._is_path_safe(abs_path)
            if not is_safe:
                return {"success": False, "error": f"无法写入: {msg}"}

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


class FileListTool(BaseTool):
    """目录列表工具"""

    def __init__(self):
        super().__init__(
            name="file_list",
            description="列出目录内容。参数: {\"dirpath\": \"目录路径\"}"
        )

    def execute(self, dirpath: str = ".", recursive: bool = False) -> Dict[str, Any]:
        try:
            abs_path = os.path.abspath(dirpath)

            if not os.path.isdir(abs_path):
                return {"success": False, "error": f"不是有效目录: {dirpath}"}

            items = []
            if recursive:
                for root, dirs, files in os.walk(abs_path):
                    for d in dirs:
                        items.append({
                            "path": os.path.join(root, d),
                            "type": "directory"
                        })
                    for f in files:
                        full_path = os.path.join(root, f)
                        items.append({
                            "path": full_path,
                            "type": "file",
                            "size": os.path.getsize(full_path)
                        })
            else:
                for item in os.listdir(abs_path):
                    full_path = os.path.join(abs_path, item)
                    is_dir = os.path.isdir(full_path)
                    items.append({
                        "name": item,
                        "type": "directory" if is_dir else "file",
                        "size": None if is_dir else os.path.getsize(full_path)
                    })

            return {
                "success": True,
                "dirpath": abs_path,
                "items": sorted(items, key=lambda x: (x.get("type") != "directory", x.get("name", x.get("path", "")))),
                "count": len(items)
            }
        except Exception as e:
            return {"success": False, "dirpath": dirpath, "error": str(e)}


class FileDeleteTool(BaseTool):
    """文件删除工具（谨慎使用）"""

    def __init__(self):
        super().__init__(
            name="file_delete",
            description="删除文件。参数: {\"filepath\": \"文件路径\"}"
        )
        self._load_config()

    def _load_config(self):
        # 从配置文件加载
        self.protected_paths = get_config_value("tools_config", "tools.file.protected_paths",
                                                ["/etc", "/usr", "/bin", "/sbin", "/boot", "/root"])

    def _is_path_safe(self, filepath: str) -> tuple:
        """检查路径安全性"""
        abs_path = os.path.abspath(filepath)

        # 获取当前用户主目录
        current_user_home = os.path.expanduser("~")

        # 允许访问用户主目录及其子目录
        if abs_path.startswith(current_user_home):
            return True, "OK"

        # 检查是否在保护路径内
        for protected in self.protected_paths:
            if abs_path.startswith(protected):
                return False, f"路径受保护: {protected}"

        return True, "OK"

    def execute(self, filepath: str) -> Dict[str, Any]:
        try:
            abs_path = os.path.abspath(filepath)

            # 安全检查
            is_safe, msg = self._is_path_safe(abs_path)
            if not is_safe:
                return {"success": False, "error": f"无法删除: {msg}"}

            if not os.path.exists(abs_path):
                return {"success": False, "error": f"文件不存在: {filepath}"}

            if os.path.isdir(abs_path):
                return {"success": False, "error": "请使用专门的目录删除工具"}

            os.remove(abs_path)
            return {
                "success": True,
                "filepath": abs_path,
                "message": f"文件已删除: {abs_path}"
            }
        except Exception as e:
            return {"success": False, "filepath": filepath, "error": str(e)}


class FileCopyTool(BaseTool):
    """文件复制工具"""

    def __init__(self):
        super().__init__(
            name="file_copy",
            description="复制文件。参数: {\"src\": \"源路径\", \"dst\": \"目标路径\"}"
        )

    def execute(self, src: str, dst: str) -> Dict[str, Any]:
        try:
            src_path = os.path.abspath(src)
            dst_path = os.path.abspath(dst)

            if not os.path.exists(src_path):
                return {"success": False, "error": f"源文件不存在: {src}"}

            # 创建目标目录
            dst_dir = os.path.dirname(dst_path)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)

            shutil.copy2(src_path, dst_path)
            return {
                "success": True,
                "src": src_path,
                "dst": dst_path,
                "message": f"文件已复制: {src_path} -> {dst_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
