"""配置管理模块

加载和管理 Agent 配置
"""

import json
import os
from typing import Dict, Any, Optional


class Config:
    """配置管理器"""

    _instance: Optional['Config'] = None

    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load()

    @classmethod
    def get_instance(cls, config_path: str = "config/config.json") -> 'Config':
        """获取配置实例（单例模式）"""
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    def load(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self._config = json.load(f)
        else:
            print(f"Warning: Config file '{self.config_path}' not found")
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点分隔符，如 'model.name'）"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        return self.get("model", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get("logging", {})

    def get_memory_config(self) -> Dict[str, Any]:
        """获取内存配置"""
        return self.get("memory", {})

    def get_tools_config(self) -> Dict[str, Any]:
        """获取工具配置"""
        return self.get("tools", {})
