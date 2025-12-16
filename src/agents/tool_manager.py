"""工具管理器

负责统一管理所有工具，提供自动发现、注册、执行等功能
解耦 Agent 和具体工具的实现

使用示例:
    from tool_manager import ToolManager

    # 获取工具管理器实例
    manager = ToolManager.get_instance()

    # 执行工具
    result = manager.execute_tool("write_file_tool", {"path": "test.txt", "content": "hello"})
    print(result)
"""

import os
import sys
import importlib
import inspect
from typing import Dict, Any, Callable, Optional
from langchain_core.tools import BaseTool

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from common.logs import Logger


class ToolManager:
    """工具管理器 - 统一管理所有工具的发现、注册和执行"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化工具管理器（只执行一次）"""
        if self._initialized:
            return

        self.logger = Logger.get_logger()
        self.tools: Dict[str, BaseTool] = {}
        self._discover_tools()

        self.logger.info(f"ToolManager initialized with {len(self.tools)} tools")
        self._initialized = True

    def _discover_tools(self):
        """自动发现并注册所有工具"""
        try:
            # 导入工具模块
            from io_tools.tools import file_tools
            from io_tools.tools import shell_tools

            # 扫描 file_tools 模块
            self._scan_module(file_tools, "io_tools.tools.file_tools")

            # 扫描 shell_tools 模块
            self._scan_module(shell_tools, "io_tools.tools.shell_tools")

            self.logger.info(f"Discovered {len(self.tools)} tools: {list(self.tools.keys())}")

        except Exception as e:
            self.logger.error(f"Failed to discover tools: {str(e)}")
            raise

    def _scan_module(self, module, module_name: str):
        """扫描模块中的所有工具"""
        for name, obj in inspect.getmembers(module):
            # 检查是否是 BaseTool 的实例（LangChain 工具）
            if isinstance(obj, BaseTool):
                self.tools[obj.name] = obj
                self.logger.debug(f"Registered tool: {obj.name} from {module_name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取指定名称的工具

        Args:
            name: 工具名称

        Returns:
            工具对象，如果不存在则返回 None
        """
        return self.tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        """列出所有可用工具及其描述

        Returns:
            工具名称到描述的映射
        """
        return {name: tool.description[:50] + "..." if len(tool.description) > 50 else tool.description
                for name, tool in self.tools.items()}

    def execute_tool(self, name: str, args: Dict[str, Any]) -> tuple[bool, str, Any]:
        """统一执行工具的接口

        Args:
            name: 工具名称
            args: 工具参数

        Returns:
            tuple: (是否成功, 结果或错误信息, 工具调用结果)
        """
        try:
            # 获取工具
            tool = self.get_tool(name)
            if not tool:
                error_msg = f"工具 '{name}' 不存在"
                self.logger.warning(error_msg)
                return False, error_msg, None

            # 执行工具
            self.logger.info(f"Executing tool: {name} with args: {args}")
            result = tool.invoke(args)

            # 记录成功
            self.logger.info(f"Tool '{name}' executed successfully")
            return True, "success", result

        except Exception as e:
            # 记录错误
            error_msg = f"工具 '{name}' 执行失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg, None

    def get_tool_names(self) -> list:
        """获取所有工具名称列表

        Returns:
            工具名称列表
        """
        return list(self.tools.keys())

    def reload_tools(self):
        """重新加载工具（用于动态添加工具）"""
        self.logger.info("Reloading tools...")
        self.tools.clear()
        self._discover_tools()
        self.logger.info(f"Tools reloaded: {len(self.tools)} tools available")

    @classmethod
    def get_instance(cls):
        """获取工具管理器实例（单例）"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# 全局工具管理器实例
tool_manager = ToolManager.get_instance()


def get_tool_manager() -> ToolManager:
    """获取工具管理器实例的便捷函数

    Returns:
        ToolManager 实例
    """
    return ToolManager.get_instance()


def execute_tool(name: str, args: Dict[str, Any]) -> tuple[bool, str, Any]:
    """便捷函数：直接执行工具

    Args:
        name: 工具名称
        args: 工具参数

    Returns:
        tuple: (是否成功, 结果或错误信息, 工具调用结果)
    """
    return tool_manager.execute_tool(name, args)


def list_available_tools() -> Dict[str, str]:
    """便捷函数：列出所有可用工具

    Returns:
        工具名称到描述的映射
    """
    return tool_manager.list_tools()
