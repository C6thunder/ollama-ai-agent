#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件操作模块
"""

import os
import shutil
from typing import Dict, Any, List, Optional


class FileOperations:
    """文件操作类"""

    PROTECTED_PATHS = ["/etc", "/usr", "/bin", "/sbin", "/boot", "/root"]

    def __init__(self, protected_paths: List[str] = None):
        self.protected_paths = protected_paths or self.PROTECTED_PATHS

    def _is_safe(self, path: str) -> tuple:
        """检查路径安全性"""
        abs_path = os.path.abspath(path)
        for protected in self.protected_paths:
            if abs_path.startswith(protected):
                return False, f"受保护路径: {protected}"
        return True, "OK"

    def list_dir(self, dirpath: str = ".",
                 recursive: bool = False) -> Dict[str, Any]:
        """列出目录内容"""
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
                        full = os.path.join(root, f)
                        items.append({
                            "path": full,
                            "type": "file",
                            "size": os.path.getsize(full)
                        })
            else:
                for item in os.listdir(abs_path):
                    full = os.path.join(abs_path, item)
                    is_dir = os.path.isdir(full)
                    items.append({
                        "name": item,
                        "type": "directory" if is_dir else "file",
                        "size": None if is_dir else os.path.getsize(full)
                    })

            return {
                "success": True,
                "dirpath": abs_path,
                "items": sorted(items, key=lambda x: (x.get("type") != "directory", x.get("name", ""))),
                "count": len(items)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy(self, src: str, dst: str) -> Dict[str, Any]:
        """复制文件"""
        try:
            src_path = os.path.abspath(src)
            dst_path = os.path.abspath(dst)

            if not os.path.exists(src_path):
                return {"success": False, "error": f"源文件不存在: {src}"}

            is_safe, msg = self._is_safe(dst_path)
            if not is_safe:
                return {"success": False, "error": msg}

            dst_dir = os.path.dirname(dst_path)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

            return {
                "success": True,
                "src": src_path,
                "dst": dst_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def move(self, src: str, dst: str) -> Dict[str, Any]:
        """移动文件"""
        try:
            src_path = os.path.abspath(src)
            dst_path = os.path.abspath(dst)

            if not os.path.exists(src_path):
                return {"success": False, "error": f"源文件不存在: {src}"}

            is_safe, msg = self._is_safe(dst_path)
            if not is_safe:
                return {"success": False, "error": msg}

            shutil.move(src_path, dst_path)

            return {
                "success": True,
                "src": src_path,
                "dst": dst_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete(self, filepath: str) -> Dict[str, Any]:
        """删除文件"""
        try:
            abs_path = os.path.abspath(filepath)

            is_safe, msg = self._is_safe(abs_path)
            if not is_safe:
                return {"success": False, "error": msg}

            if not os.path.exists(abs_path):
                return {"success": False, "error": f"文件不存在: {filepath}"}

            if os.path.isdir(abs_path):
                shutil.rmtree(abs_path)
            else:
                os.remove(abs_path)

            return {
                "success": True,
                "filepath": abs_path,
                "message": "已删除"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def exists(self, filepath: str) -> Dict[str, Any]:
        """检查文件是否存在"""
        abs_path = os.path.abspath(filepath)
        exists = os.path.exists(abs_path)
        return {
            "success": True,
            "filepath": abs_path,
            "exists": exists,
            "is_file": os.path.isfile(abs_path) if exists else False,
            "is_dir": os.path.isdir(abs_path) if exists else False
        }

    def info(self, filepath: str) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            abs_path = os.path.abspath(filepath)

            if not os.path.exists(abs_path):
                return {"success": False, "error": f"文件不存在: {filepath}"}

            stat = os.stat(abs_path)
            return {
                "success": True,
                "filepath": abs_path,
                "size": stat.st_size,
                "is_file": os.path.isfile(abs_path),
                "is_dir": os.path.isdir(abs_path),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
