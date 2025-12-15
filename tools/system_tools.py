#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统信息工具模块
"""

import os
import sys
import platform
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.memory_agent import BaseTool


class SystemInfoTool(BaseTool):
    """系统信息工具"""

    def __init__(self):
        super().__init__(
            name="system_info",
            description="获取系统信息。参数: {\"info_type\": \"platform|python|env|all\"}"
        )

    def execute(self, info_type: str = "all") -> Dict[str, Any]:
        try:
            if info_type == "platform":
                return {
                    "success": True,
                    "info_type": "platform",
                    "data": {
                        "system": platform.system(),
                        "release": platform.release(),
                        "version": platform.version(),
                        "machine": platform.machine(),
                        "processor": platform.processor(),
                        "platform": platform.platform()
                    }
                }

            elif info_type == "python":
                return {
                    "success": True,
                    "info_type": "python",
                    "data": {
                        "version": sys.version,
                        "version_info": {
                            "major": sys.version_info.major,
                            "minor": sys.version_info.minor,
                            "micro": sys.version_info.micro
                        },
                        "executable": sys.executable,
                        "prefix": sys.prefix
                    }
                }

            elif info_type == "env":
                safe_vars = ["PATH", "HOME", "USER", "SHELL", "LANG", "PWD", "TERM", "EDITOR"]
                return {
                    "success": True,
                    "info_type": "env",
                    "data": {
                        "cwd": os.getcwd(),
                        "environment": {k: os.getenv(k) for k in safe_vars if os.getenv(k)}
                    }
                }

            elif info_type == "all":
                return {
                    "success": True,
                    "info_type": "all",
                    "data": {
                        "platform": {
                            "system": platform.system(),
                            "release": platform.release(),
                            "machine": platform.machine()
                        },
                        "python": {
                            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                        },
                        "cwd": os.getcwd(),
                        "user": os.getenv("USER", "unknown")
                    }
                }

            else:
                return {
                    "success": False,
                    "error": f"不支持的信息类型: {info_type}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}


class DiskUsageTool(BaseTool):
    """磁盘使用情况工具"""

    def __init__(self):
        super().__init__(
            name="disk_usage",
            description="获取磁盘使用情况。参数: {\"path\": \"路径\"}"
        )

    def execute(self, path: str = "/") -> Dict[str, Any]:
        try:
            usage = os.statvfs(path)
            total = usage.f_blocks * usage.f_frsize
            free = usage.f_bfree * usage.f_frsize
            used = total - free
            percent = (used / total) * 100 if total > 0 else 0

            return {
                "success": True,
                "path": path,
                "total_bytes": total,
                "used_bytes": used,
                "free_bytes": free,
                "percent_used": round(percent, 2),
                "total_gb": round(total / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2)
            }
        except Exception as e:
            return {"success": False, "path": path, "error": str(e)}


class ProcessListTool(BaseTool):
    """进程列表工具"""

    def __init__(self):
        super().__init__(
            name="process_list",
            description="获取当前用户的进程列表。无需参数。"
        )

    def execute(self) -> Dict[str, Any]:
        try:
            import subprocess
            result = subprocess.run(
                ["ps", "-u", os.getenv("USER", ""), "-o", "pid,ppid,comm,%cpu,%mem"],
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            processes = []
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 5:
                        processes.append({
                            "pid": parts[0],
                            "ppid": parts[1],
                            "command": parts[2],
                            "cpu": parts[3],
                            "mem": parts[4]
                        })

            return {
                "success": True,
                "processes": processes[:20],  # 限制数量
                "count": len(processes)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
