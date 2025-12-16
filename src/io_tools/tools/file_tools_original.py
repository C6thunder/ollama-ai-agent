"""文件操作工具（配置驱动版）

提供文件创建、写入、读取等操作（基于配置的安全验证）
"""

from langchain.tools import tool
import os
from typing import Dict, Any
import sys

# 添加 src 目录到路径以导入 security
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from security.security import SecurityValidator


@tool
def write_file_tool(path: str, content: str) -> str:
    """Write content to a file at the given path (配置驱动版)

    Args:
        path: The file path to write to
        content: The content to write

    Returns:
        A success message indicating the file was written
    """
    # 安全验证
    is_safe, error = SecurityValidator.validate_path(path, check_write=True)
    if not is_safe:
        return f"错误: {error}"

    # 检查文件扩展名
    from security.security import SecurityConfig
    allowed_exts = SecurityConfig.get('tools.file.allowed_extensions', [])
    blocked_exts = SecurityConfig.get('tools.file.blocked_extensions', [])

    # 获取文件扩展名
    _, ext = os.path.splitext(path)

    # 检查是否在禁止列表中
    if ext in blocked_exts:
        return f"错误: 不允许创建 {ext} 类型的文件"

    # 如果配置了允许列表，检查是否在其中
    if allowed_exts and ext not in allowed_exts:
        return f"错误: 不允许创建 {ext} 类型的文件"

    try:
        # 清理文件名
        sanitized_path = SecurityValidator.sanitize_filename(path)

        # 创建目录
        dir_path = os.path.dirname(sanitized_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # 检查文件大小
        max_file_size = SecurityValidator._get_max_file_size()
        if len(content) > max_file_size:
            return f"错误: 文件内容过大 (最大 {max_file_size} 字节)"

        # 写入文件
        with open(sanitized_path, "w", encoding='utf-8') as f:
            f.write(content)

        return f"Successfully wrote file: {sanitized_path}"
    except Exception as e:
        return f"错误: 写入文件失败 - {str(e)}"


@tool
def read_file_tool(path: str) -> str:
    """Read content from a file at the given path (配置驱动版)

    Args:
        path: The file path to read from

    Returns:
        The content of the file
    """
    # 安全验证
    is_safe, error = SecurityValidator.validate_path(path, check_write=False)
    if not is_safe:
        return f"错误: {error}"

    # 检查文件扩展名
    from security.security import SecurityConfig
    blocked_exts = SecurityConfig.get('tools.file.blocked_extensions', [])

    # 获取文件扩展名
    _, ext = os.path.splitext(path)

    # 检查是否在禁止列表中
    if ext in blocked_exts:
        return f"错误: 不允许读取 {ext} 类型的文件"

    try:
        # 清理文件名
        sanitized_path = SecurityValidator.sanitize_filename(path)

        with open(sanitized_path, "r", encoding='utf-8') as f:
            content = f.read()

        # 限制读取大小（防止读取大文件）
        max_read_size = SecurityValidator._get_max_read_size()
        if len(content) > max_read_size:
            content = content[:max_read_size] + "\n... (文件过大，已截断)"

        return content
    except FileNotFoundError:
        return f"错误: 文件 '{path}' 未找到"
    except Exception as e:
        return f"错误: 读取文件失败 - {str(e)}"


@tool
def list_files_tool(directory: str = ".") -> str:
    """List files in a directory (配置驱动版)

    Args:
        directory: The directory to list (default: current directory)

    Returns:
        A list of files in the directory
    """
    # 安全验证
    is_safe, error = SecurityValidator.validate_path(directory, check_write=False)
    if not is_safe:
        return f"错误: {error}"

    try:
        # 清理目录名
        sanitized_dir = SecurityValidator.sanitize_filename(directory)

        files = os.listdir(sanitized_dir)

        # 限制返回数量
        files = SecurityValidator.limit_file_list(files)

        return "\n".join(files) if files else "目录为空"
    except FileNotFoundError:
        return f"错误: 目录 '{directory}' 未找到"
    except Exception as e:
        return f"错误: 列出目录失败 - {str(e)}"
