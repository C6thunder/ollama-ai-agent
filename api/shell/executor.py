#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell 命令执行模块
"""

import os
import subprocess
import shlex
from typing import Dict, Any, List, Optional


class ShellExecutor:
    """Shell 命令执行器"""

    SAFE_COMMANDS = [
        "ls", "pwd", "whoami", "date", "cal", "uptime",
        "cat", "head", "tail", "wc", "grep", "find",
        "echo", "printf", "which", "whereis", "type",
        "df", "du", "free", "top", "ps", "uname",
        "id", "groups", "hostname", "env", "printenv",
        "file", "stat", "md5sum", "sha256sum",
        "tree", "realpath", "dirname", "basename"
    ]

    DANGEROUS_PATTERNS = [
        "rm -rf /", "rm -rf /*", "mkfs", "dd if=/dev/zero",
        ":(){ :|:& };:", "chmod -R 777 /",
        "shutdown", "reboot", "halt",
        "> /dev/sda", "| sh", "| bash"
    ]

    def __init__(self, working_dir: str = None, timeout: int = 30):
        self.working_dir = working_dir or os.getcwd()
        self.timeout = timeout
        self.history: List[Dict] = []

    def is_safe(self, cmd: str) -> tuple:
        """检查命令安全性"""
        cmd_lower = cmd.lower().strip()
        if not cmd_lower:
            return False, "命令为空"

        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in cmd_lower:
                return False, f"危险命令: {pattern}"

        return True, "OK"

    def execute(self, command: str, timeout: int = None,
                cwd: str = None) -> Dict[str, Any]:
        """执行命令"""
        is_safe, msg = self.is_safe(command)
        if not is_safe:
            return {
                "success": False,
                "command": command,
                "error": msg
            }

        work_dir = cwd or self.working_dir
        timeout = timeout or self.timeout

        # 检查是否需要 shell 模式
        shell_chars = ['>', '<', '|', '&&', '||', ';', '$', '`']
        use_shell = any(c in command for c in shell_chars)

        try:
            if use_shell:
                result = subprocess.run(
                    command, shell=True,
                    capture_output=True, text=True,
                    timeout=timeout, cwd=work_dir
                )
            else:
                result = subprocess.run(
                    shlex.split(command),
                    capture_output=True, text=True,
                    timeout=timeout, cwd=work_dir
                )

            output = {
                "success": result.returncode == 0,
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            self.history.append(output)
            return output

        except subprocess.TimeoutExpired:
            return {"success": False, "command": command, "error": "超时"}
        except FileNotFoundError:
            return {"success": False, "command": command, "error": "命令未找到"}
        except Exception as e:
            return {"success": False, "command": command, "error": str(e)}

    def get_history(self) -> List[Dict]:
        """获取执行历史"""
        return self.history

    def clear_history(self):
        """清空历史"""
        self.history.clear()
