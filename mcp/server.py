#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 服务器实现
提供 MCP (Model Context Protocol) 服务器功能
"""

import json
import asyncio
import sys
from typing import Dict, Any, List, Optional
from .tools import MCPTool, get_all_tools


class MCPServer:
    """MCP 服务器"""

    def __init__(self, name: str = "AI-Agent MCP Server", version: str = "1.0.0"):
        """
        初始化 MCP 服务器

        Args:
            name: 服务器名称
            version: 服务器版本
        """
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """注册默认工具"""
        default_tools = get_all_tools()
        for tool in default_tools:
            self.register_tool(tool)

    def register_tool(self, tool: MCPTool):
        """
        注册 MCP 工具

        Args:
            tool: MCP 工具实例
        """
        self.tools[tool.name] = tool

    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "name": self.name,
            "version": self.version,
            "protocolVersion": "2024-11-05"
        }

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """获取工具列表"""
        return [tool.to_dict() for tool in self.tools.values()]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用工具

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        if name not in self.tools:
            return {
                "success": False,
                "error": f"工具不存在: {name}"
            }

        tool = self.tools[name]

        try:
            result = tool.execute(**arguments)
            return {
                "success": True,
                "tool": name,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "tool": name,
                "error": str(e)
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理 MCP 请求

        Args:
            request: MCP 请求对象

        Returns:
            MCP 响应对象
        """
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "initialize":
                # 初始化请求
                response = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": self.name,
                        "version": self.version
                    }
                }

            elif method == "tools/list":
                # 获取工具列表
                response = {
                    "tools": self.get_tools_list()
                }

            elif method == "tools/call":
                # 调用工具
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})

                result = self.call_tool(tool_name, tool_arguments)

                response = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2)
                        }
                    ],
                    "isError": not result["success"]
                }

            else:
                response = {
                    "error": {
                        "code": -32601,
                        "message": f"方法不存在: {method}"
                    }
                }

            # 添加请求 ID（如果存在）
            if request_id is not None:
                response["id"] = request_id

            return response

        except Exception as e:
            error_response = {
                "error": {
                    "code": -32603,
                    "message": f"内部错误: {str(e)}"
                },
                "id": request.get("id")
            }
            return error_response

    async def run_stdio(self):
        """通过标准输入/输出运行服务器"""
        try:
            while True:
                # 从标准输入读取请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, input
                )

                if not line:
                    break

                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)

                    # 输出响应到标准输出
                    print(json.dumps(response, ensure_ascii=False))

                except json.JSONDecodeError as e:
                    error_response = {
                        "error": {
                            "code": -32700,
                            "message": f"JSON 解析错误: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False))

                except Exception as e:
                    error_response = {
                        "error": {
                            "code": -32603,
                            "message": f"处理错误: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response, ensure_ascii=False))

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"服务器错误: {e}", file=sys.stderr)

    def create_stdio_server(self):
        """创建标准输入/输出服务器"""
        return self


class AsyncMCPServer:
    """异步 MCP 服务器"""

    def __init__(self, name: str = "AI-Agent Async MCP Server", version: str = "1.0.0"):
        """
        初始化异步 MCP 服务器

        Args:
            name: 服务器名称
            version: 服务器版本
        """
        self.server = MCPServer(name, version)
        self.request_handlers: Dict[str, callable] = {}

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理 MCP 请求"""
        return await self.server.handle_request(request)

    def add_custom_handler(self, method: str, handler: callable):
        """
        添加自定义请求处理器

        Args:
            method: 方法名
            handler: 处理器函数
        """
        self.request_handlers[method] = handler

    async def run(self):
        """运行服务器"""
        print(f"启动 {self.server.name} v{self.server.version}")
        print("按 Ctrl+C 停止服务器")

        try:
            await self.server.run_stdio()
        except KeyboardInterrupt:
            print("\n服务器已停止")


# CLI 入口点
if __name__ == "__main__":
    import sys

    # 创建并运行 MCP 服务器
    server = AsyncMCPServer()
    asyncio.run(server.run())