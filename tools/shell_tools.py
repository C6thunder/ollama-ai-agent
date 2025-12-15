#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell 工具模块
提供安全的终端命令执行功能
"""

import os
import subprocess
import shlex
from typing import Dict, Any, List, Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.memory_agent import BaseTool
from core import get_config_value


class ShellTool(BaseTool):
    """Shell 命令执行工具"""

    # 安全命令白名单（快捷命令）
    SAFE_COMMANDS = [
        "ls", "pwd", "whoami", "date", "cal", "uptime",
        "cat", "head", "tail", "wc", "grep", "find",
        "echo", "printf", "which", "whereis", "type",
        "df", "du", "free", "top", "ps", "uname",
        "id", "groups", "hostname", "env", "printenv",
        "file", "stat", "md5sum", "sha256sum",
        "tree", "realpath", "dirname", "basename",
        "sort", "uniq", "cut", "tr",
        "diff", "comm", "join", "paste",
        "tar", "gzip", "gunzip", "zip", "unzip",
        "git", "python", "python3", "pip", "node", "npm"
    ]

    # 危险命令黑名单
    DANGEROUS_PATTERNS = [
        "rm -rf /", "rm -rf /*", "rm -r /",
        "mkfs", "dd if=/dev/zero", "dd of=/dev",
        ":(){ :|:& };:", "chmod -R 777 /", "chown -R",
        "shutdown", "reboot", "halt", "init 0", "init 6",
        "kill -9 -1", "pkill -9 -1", "> /dev/sda",
        "mv /* /dev/null", "wget | sh", "curl | bash",
        ">/dev/sda", "| sh", "| bash"
    ]

    def __init__(self, working_dir: Optional[str] = None):
        super().__init__(
            name="shell",
            description="执行终端命令。参数: {\"command\": \"命令\"}"
        )
        self.working_dir = working_dir or os.getcwd()
        self.execution_history: List[Dict[str, Any]] = []

        # 从配置文件加载
        self.timeout = get_config_value("tools_config", "tools.shell.timeout", 30)

    def is_safe(self, cmd: str) -> tuple:
        """
        检查命令安全性

        Returns:
            (is_safe, message)
        """
        cmd_lower = cmd.lower().strip()

        if not cmd_lower:
            return False, "命令不能为空"

        # 检查危险模式
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in cmd_lower:
                return False, f"检测到危险命令模式: {pattern}"

        return True, "OK"

    def execute(self, command: str, timeout: int = None, cwd: str = None) -> Dict[str, Any]:
        """
        执行 Shell 命令

        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            cwd: 工作目录

        Returns:
            执行结果字典
        """
        # 安全检查
        is_safe, msg = self.is_safe(command)
        if not is_safe:
            return {
                "success": False,
                "command": command,
                "error": msg,
                "stdout": "",
                "stderr": msg
            }

        work_dir = cwd or self.working_dir
        timeout = timeout or self.timeout

        # 检查是否需要 shell 模式（包含重定向、管道等）
        shell_chars = ['>', '<', '|', '&&', '||', ';', '$', '`']
        use_shell = any(c in command for c in shell_chars)

        try:
            if use_shell:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=work_dir
                )
            else:
                result = subprocess.run(
                    shlex.split(command),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=work_dir
                )

            output = {
                "success": result.returncode == 0,
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "working_dir": work_dir
            }

            self.execution_history.append(output)
            return output

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "command": command,
                "error": f"命令超时 ({timeout}秒)",
                "stdout": "",
                "stderr": f"Timeout after {timeout}s"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "command": command,
                "error": f"命令未找到: {command.split()[0]}",
                "stdout": "",
                "stderr": "Command not found"
            }
        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }


class PwdTool(BaseTool):
    """获取当前工作目录"""

    def __init__(self):
        super().__init__(
            name="pwd",
            description="获取当前工作目录，无需参数"
        )

    def execute(self) -> Dict[str, Any]:
        return {
            "success": True,
            "cwd": os.getcwd()
        }


class WhoamiTool(BaseTool):
    """获取当前用户"""

    def __init__(self):
        super().__init__(
            name="whoami",
            description="获取当前用户名，无需参数"
        )

    def execute(self) -> Dict[str, Any]:
        return {
            "success": True,
            "user": os.getenv("USER", os.getenv("USERNAME", "unknown"))
        }


class DateTool(BaseTool):
    """获取当前日期时间"""

    def __init__(self):
        super().__init__(
            name="date",
            description="获取当前日期时间，无需参数"
        )

    def execute(self, format: str = "%Y-%m-%d %H:%M:%S") -> Dict[str, Any]:
        from datetime import datetime
        return {
            "success": True,
            "datetime": datetime.now().strftime(format),
            "timestamp": datetime.now().timestamp()
        }


class LsTool(BaseTool):
    """列出目录内容"""

    def __init__(self):
        super().__init__(
            name="ls",
            description="列出目录内容。参数: {\"path\": \"目录路径\"}"
        )

    def execute(self, path: str = ".") -> Dict[str, Any]:
        try:
            items = os.listdir(path)
            detailed = []
            for item in items:
                full_path = os.path.join(path, item)
                is_dir = os.path.isdir(full_path)
                detailed.append({
                    "name": item,
                    "type": "directory" if is_dir else "file",
                    "size": os.path.getsize(full_path) if not is_dir else None
                })
            return {
                "success": True,
                "path": os.path.abspath(path),
                "items": sorted(detailed, key=lambda x: (x["type"] != "directory", x["name"])),
                "count": len(items)
            }
        except Exception as e:
            return {
                "success": False,
                "path": path,
                "error": str(e)
            }


class EnvTool(BaseTool):
    """获取环境变量"""

    def __init__(self):
        super().__init__(
            name="env",
            description="获取环境变量。参数: {\"name\": \"变量名\"} 或无参数获取所有"
        )

    def execute(self, name: str = None) -> Dict[str, Any]:
        if name:
            value = os.getenv(name)
            return {
                "success": value is not None,
                "name": name,
                "value": value,
                "error": None if value else f"环境变量 {name} 不存在"
            }
        else:
            # 返回安全的环境变量子集
            safe_vars = ["PATH", "HOME", "USER", "SHELL", "LANG", "PWD", "TERM"]
            env_dict = {k: os.getenv(k) for k in safe_vars if os.getenv(k)}
            return {
                "success": True,
                "environment": env_dict,
                "count": len(env_dict)
            }
