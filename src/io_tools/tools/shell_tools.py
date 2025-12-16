"""Shell 命令工具（LangChain 1.2 优化版）

利用 LangChain 的内置功能，提供更好的命令验证和错误处理
"""

from langchain.tools import tool
from langchain_core.tools import ToolException
import subprocess
import os
import sys

# 添加 src 目录到路径以导入 security
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from security.security import SecurityValidator, SecurityConfig


class ShellCommandException(ToolException):
    """Shell 命令异常 - 提供更详细的错误信息"""
    pass


@tool
def shell_command_tool(cmd: str) -> str:
    """Execute a shell command with security validation (LangChain 优化版)

    Args:
        cmd: The shell command to execute

    Returns:
        The output of the command

    Raises:
        ShellCommandException: When command validation fails or execution fails
    """
    # 1. 命令安全验证
    is_safe, error = SecurityValidator.validate_shell_command(cmd)
    if not is_safe:
        raise ShellCommandException(f"命令验证失败: {error}")

    # 2. 超时时间检查
    timeout = SecurityValidator._get_command_timeout()

    # 3. 工作目录限制
    allowed_base_dir = SecurityValidator._get_allowed_base_dir()

    try:
        # 4. 执行命令
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=allowed_base_dir,
            env={"HOME": allowed_base_dir}
        )

        # 5. 检查返回码
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            raise ShellCommandException(f"命令执行失败 (返回码 {result.returncode}): {error_msg}")

        # 6. 限制输出大小
        output = result.stdout
        max_output_size = SecurityValidator._get_max_output_size()
        if len(output) > max_output_size:
            output = output[:max_output_size] + "\n... (输出过大，已截断)"

        return output if output else "命令执行成功"

    except subprocess.TimeoutExpired:
        raise ShellCommandException(f"命令执行超时 (>{timeout} 秒)")
    except Exception as e:
        raise ShellCommandException(f"命令执行失败: {str(e)}")


@tool
def get_working_directory_tool() -> str:
    """Get the current working directory (LangChain 优化版)

    Returns:
        The current working directory
    """
    return os.getcwd()


@tool
def list_directory_tool(directory: str = ".") -> str:
    """List files in a directory (LangChain 优化版)

    Args:
        directory: The directory to list

    Returns:
        A list of files in the directory

    Raises:
        ShellCommandException: When directory validation fails
    """
    # 1. 目录安全验证
    is_safe, error = SecurityValidator.validate_path(directory, check_write=False)
    if not is_safe:
        raise ShellCommandException(f"目录验证失败: {error}")

    try:
        # 使用 realpath 获取实际路径，不使用 sanitize_filename
        real_path = os.path.realpath(directory)

        if not os.path.exists(real_path):
            raise ShellCommandException(f"目录 '{directory}' 不存在")

        if not os.path.isdir(real_path):
            raise ShellCommandException(f"'{directory}' 不是一个目录")

        files = os.listdir(real_path)
        return "\n".join(sorted(files))
    except Exception as e:
        raise ShellCommandException(f"列出目录失败: {str(e)}")
