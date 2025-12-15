#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件 API 模块
"""

from .reader import FileReader
from .writer import FileWriter
from .operations import FileOperations


class FileAPI:
    """
    文件 API 统一入口
    兼容原有接口
    """

    def __init__(self, max_file_size: int = 10 * 1024 * 1024):
        self.reader = FileReader(max_file_size)
        self.writer = FileWriter()
        self.ops = FileOperations()

    def read_file(self, filepath: str, encoding: str = "utf-8"):
        """读取文件"""
        return self.reader.read(filepath, encoding)

    def write_file(self, filepath: str, content: str, encoding: str = "utf-8"):
        """写入文件"""
        return self.writer.write(filepath, content, encoding)

    def append_file(self, filepath: str, content: str):
        """追加内容"""
        return self.writer.append(filepath, content)

    def read_json(self, filepath: str):
        """读取 JSON 文件"""
        import json
        result = self.reader.read(filepath)
        if result["success"]:
            try:
                result["data"] = json.loads(result["content"])
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"JSON 解析错误: {e}"}
        return result

    def write_json(self, filepath: str, data, indent: int = 2):
        """写入 JSON 文件"""
        return self.writer.write_json(filepath, data, indent)

    def list_directory(self, dirpath: str = ".", recursive: bool = False):
        """列出目录"""
        return self.ops.list_dir(dirpath, recursive)

    def copy_file(self, src: str, dst: str):
        """复制文件"""
        return self.ops.copy(src, dst)

    def move_file(self, src: str, dst: str):
        """移动文件"""
        return self.ops.move(src, dst)

    def delete_file(self, filepath: str):
        """删除文件"""
        return self.ops.delete(filepath)

    def file_exists(self, filepath: str):
        """检查文件是否存在"""
        return self.ops.exists(filepath)

    def get_file_info(self, filepath: str):
        """获取文件信息"""
        return self.ops.info(filepath)


__all__ = [
    'FileAPI',
    'FileReader',
    'FileWriter',
    'FileOperations'
]
