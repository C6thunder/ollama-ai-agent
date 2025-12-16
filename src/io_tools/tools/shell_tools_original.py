"""Shell 命令工具（配置驱动版）

提供执行安全 Shell 命令的功能（基于配置）
"""

from langchain.tools import tool
import subprocess
import os
from typing import Optional
import sys

# 添加 src 目录到路径以导入 security
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from security.security import SecurityValidator


@tool
def shell_command_tool(cmd: str) -> str:
    """Execute a shell command and return the output (配置驱动版)

    Args:
        cmd: The shell command to execute

    Returns:
        The output of the command
    """
    # 安全验证
    is_safe, error = SecurityValidator.validate_shell_command(cmd)
    if not is_safe:
        return f"错误: {error}"

    try:
        # 获取超时时间
        timeout = SecurityValidator._get_command_timeout()

        # 获取允许的基础目录
        base_dir = SecurityValidator._get_allowed_base_dir()

        result = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            timeout=timeout,
            cwd=base_dir
        )

        # 限制输出大小
        result = SecurityValidator.limit_output_size(result)

        return result
    except subprocess.CalledProcessError as e:
        return f"命令执行失败 (退出码: {e.returncode}):\n{e.output}"
    except subprocess.TimeoutExpired:
        timeout = SecurityValidator._get_command_timeout()
        return f"错误: 命令执行超时 ({timeout}秒)"
    except Exception as e:
        return f"错误: 执行命令失败 - {str(e)}"


@tool
def get_current_directory_tool() -> str:
    """Get the current working directory (配置驱动版)

    Returns:
        The current working directory path
    """
    try:
        cwd = os.getcwd()
        # 只返回允许的目录
        real_cwd = os.path.realpath(cwd)
        real_base = os.path.realpath(SecurityValidator._get_allowed_base_dir())

        if real_cwd.startswith(real_base):
            return real_cwd
        else:
            return SecurityValidator._get_allowed_base_dir()
    except Exception as e:
        return f"错误: 获取当前目录失败 - {str(e)}"
