#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器
从 config 文件夹加载配置文件
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_dir: str = "config"):
        """
        初始化配置加载器

        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, Any] = {}

    def load(self, config_name: str) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            config_name: 配置文件名（不含扩展名）

        Returns:
            配置字典
        """
        if config_name in self._configs:
            return self._configs[config_name]

        config_file = self.config_dir / f"{config_name}.json"

        if not config_file.exists():
            print(f"警告: 配置文件 {config_file} 不存在，使用默认配置")
            return self._get_default_config(config_name)

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._configs[config_name] = config
                return config
        except Exception as e:
            print(f"警告: 加载配置文件 {config_file} 失败: {e}")
            return self._get_default_config(config_name)

    def _get_default_config(self, config_name: str) -> Dict[str, Any]:
        """获取默认配置"""
        defaults = {
            "agent_config": {
                "agent": {
                    "max_iterations": 10,
                    "verbose": True
                },
                "model": {
                    "name": "qwen2.5:7b",
                    "host": "127.0.0.1",
                    "port": 11434,
                    "temperature": 0.7
                }
            },
            "tools_config": {
                "tools": {
                    "file": {
                        "max_file_size": 10485760,
                        "protected_paths": ["/etc", "/usr", "/bin", "/sbin", "/boot", "/root"]
                    },
                    "shell": {
                        "timeout": 30,
                        "safe_commands": [],
                        "dangerous_commands": []
                    },
                    "network": {
                        "timeout": 30,
                        "max_retries": 3
                    }
                }
            }
        }

        return defaults.get(config_name, {})

    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            config_name: 配置文件名
            key: 配置键（支持点号分隔，如 "model.name"）
            default: 默认值

        Returns:
            配置值
        """
        config = self.load(config_name)

        # 支持点号分隔的键
        keys = key.split('.')
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def reload(self, config_name: Optional[str] = None):
        """
        重新加载配置

        Args:
            config_name: 配置文件名，为空则重新加载所有
        """
        if config_name:
            if config_name in self._configs:
                del self._configs[config_name]
        else:
            self._configs.clear()


# 全局配置加载器实例
_loader = None


def get_config_loader() -> ConfigLoader:
    """获取全局配置加载器实例"""
    global _loader
    if _loader is None:
        _loader = ConfigLoader()
    return _loader


def load_config(config_name: str) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_name: 配置文件名

    Returns:
        配置字典
    """
    return get_config_loader().load(config_name)


def get_config_value(config_name: str, key: str, default: Any = None) -> Any:
    """
    获取配置值

    Args:
        config_name: 配置文件名
        key: 配置键
        default: 默认值

    Returns:
        配置值
    """
    return get_config_loader().get(config_name, key, default)


def get_agent_config() -> Dict[str, Any]:
    """获取 Agent 配置"""
    return load_config("agent_config")


def get_tools_config() -> Dict[str, Any]:
    """获取工具配置"""
    return load_config("tools_config")


def get_prompts_config() -> Dict[str, Any]:
    """获取提示词配置"""
    return load_config("prompts")


def get_tool_descriptions_config() -> Dict[str, Any]:
    """获取工具描述配置"""
    return load_config("tool_descriptions")
