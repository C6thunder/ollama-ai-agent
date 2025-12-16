"""文件操作工具（LangChain 1.2 优化版）

利用 LangChain 的内置功能，提供更好的错误处理和安全性
"""

from langchain.tools import tool
from langchain_core.tools import ToolException
import os
import sys

# 添加 src 目录到路径以导入 security
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from security.security import SecurityValidator, SecurityConfig


class SecurityToolException(ToolException):
    """安全工具异常 - 提供更详细的错误信息"""
    pass


@tool
def write_file_tool(path: str, content: str) -> str:
    """Write content to a file at the given path (LangChain 优化版)

    Args:
        path: The file path to write to
        content: The content to write

    Returns:
        A success message indicating the file was written

    Raises:
        SecurityToolException: When path validation fails
    """
    # 1. 路径安全验证
    is_safe, error = SecurityValidator.validate_path(path, check_write=True)
    if not is_safe:
        raise SecurityToolException(f"路径验证失败: {error}")

    # 2. 文件扩展名检查
    allowed_exts = SecurityConfig.get('tools.file.allowed_extensions', [])
    blocked_exts = SecurityConfig.get('tools.file.blocked_extensions', [])
    _, ext = os.path.splitext(path)

    if ext in blocked_exts:
        raise SecurityToolException(f"不允许创建 {ext} 类型的文件")

    if allowed_exts and ext not in allowed_exts:
        raise SecurityToolException(f"不允许创建 {ext} 类型的文件")

    # 3. 文件大小检查
    max_file_size = SecurityValidator._get_max_file_size()
    if len(content) > max_file_size:
        raise SecurityToolException(f"文件内容过大 (最大 {max_file_size} 字节)")

    # 4. 执行文件写入
    try:
        # 使用 realpath 获取实际路径（已经通过安全验证，不需要 sanitize）
        real_path = os.path.realpath(path)
        dir_path = os.path.dirname(real_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(real_path, "w", encoding='utf-8') as f:
            f.write(content)

        return f"Successfully wrote file: {real_path}"
    except Exception as e:
        raise SecurityToolException(f"写入文件失败: {str(e)}")


@tool
def read_file_tool(path: str) -> str:
    """Read content from a file at the given path (LangChain 优化版)

    Args:
        path: The file path to read from

    Returns:
        The content of the file

    Raises:
        SecurityToolException: When path validation fails or file not found
    """
    # 1. 路径安全验证
    is_safe, error = SecurityValidator.validate_path(path, check_write=False)
    if not is_safe:
        raise SecurityToolException(f"路径验证失败: {error}")

    # 2. 文件扩展名检查
    blocked_exts = SecurityConfig.get('tools.file.blocked_extensions', [])
    _, ext = os.path.splitext(path)

    if ext in blocked_exts:
        raise SecurityToolException(f"不允许读取 {ext} 类型的文件")

    # 3. 读取文件
    try:
        # 使用 realpath 获取实际路径（已经通过安全验证，不需要 sanitize）
        real_path = os.path.realpath(path)

        with open(real_path, "r", encoding='utf-8') as f:
            content = f.read()

        # 4. 限制读取大小
        max_read_size = SecurityValidator._get_max_read_size()
        if len(content) > max_read_size:
            content = content[:max_read_size] + "\n... (文件过大，已截断)"

        return content
    except FileNotFoundError:
        raise SecurityToolException(f"文件 '{path}' 未找到")
    except Exception as e:
        raise SecurityToolException(f"读取文件失败: {str(e)}")


@tool
def list_files_tool(directory: str = ".") -> str:
    """List files in a directory (LangChain 优化版)

    Args:
        directory: The directory to list (default: current directory)

    Returns:
        A list of files in the directory

    Raises:
        SecurityToolException: When directory validation fails
    """
    # 1. 目录安全验证
    is_safe, error = SecurityValidator.validate_path(directory, check_write=False)
    if not is_safe:
        raise SecurityToolException(f"目录验证失败: {error}")

    # 2. 执行目录列表
    try:
        # 使用 realpath 获取实际路径，不使用 sanitize_filename
        real_path = os.path.realpath(directory)

        if not os.path.exists(real_path):
            raise SecurityToolException(f"目录 '{directory}' 不存在")

        if not os.path.isdir(real_path):
            raise SecurityToolException(f"'{directory}' 不是一个目录")

        files = os.listdir(real_path)

        # 3. 限制文件数量
        max_files = SecurityConfig.get('security.max_files_list', 200)
        if len(files) > max_files:
            files = files[:max_files]

        return "\n".join(files)
    except Exception as e:
        raise SecurityToolException(f"列出文件失败: {str(e)}")


@tool
def delete_file_tool(path: str) -> str:
    """Delete a file (LangChain 优化版)

    Args:
        path: The file path to delete

    Returns:
        A success message indicating the file was deleted

    Raises:
        SecurityToolException: When deletion is not allowed or fails
    """
    # 1. 路径安全验证
    is_safe, error = SecurityValidator.validate_path(path, check_write=True)
    if not is_safe:
        raise SecurityToolException(f"路径验证失败: {error}")

    # 2. 执行文件删除
    try:
        # 使用 realpath 获取实际路径（已经通过安全验证，不需要 sanitize）
        real_path = os.path.realpath(path)

        if not os.path.exists(real_path):
            raise SecurityToolException(f"文件 '{path}' 不存在")

        if os.path.isdir(real_path):
            raise SecurityToolException(f"'{path}' 是一个目录，不能使用删除文件工具")

        os.remove(real_path)
        return f"Successfully deleted file: {real_path}"
    except Exception as e:
        raise SecurityToolException(f"删除文件失败: {str(e)}")
