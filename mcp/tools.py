#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 工具定义
提供各种 MCP 工具实现
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class MCPTool(ABC):
    """MCP 工具基类"""

    def __init__(self, name: str, description: str):
        """
        初始化 MCP 工具

        Args:
            name: 工具名称
            description: 工具描述
        """
        self.name = name
        self.description = description

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """获取工具的 JSON Schema"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具操作"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.get_schema()
        }


class ShellTool(MCPTool):
    """Shell 命令工具"""

    def __init__(self):
        super().__init__(
            name="shell",
            description="执行 shell 命令"
        )

    def get_schema(self) -> Dict[str, Any]:
        """获取 Shell 工具的 JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的 shell 命令"
                },
                "working_directory": {
                    "type": "string",
                    "description": "工作目录（可选）",
                    "default": "."
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "是否捕获输出",
                    "default": True
                }
            },
            "required": ["command"]
        }

    def execute(self, command: str, working_directory: str = ".", capture_output: bool = True) -> Dict[str, Any]:
        """
        执行 shell 命令

        Args:
            command: 要执行的命令
            working_directory: 工作目录
            capture_output: 是否捕获输出

        Returns:
            执行结果
        """
        try:
            import subprocess
            import shlex

            result = subprocess.run(
                shlex.split(command),
                capture_output=capture_output,
                text=True,
                cwd=working_directory,
                check=False
            )

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "command": command,
                "working_directory": working_directory
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }


class FileTool(MCPTool):
    """文件操作工具"""

    def __init__(self):
        super().__init__(
            name="file",
            description="文件操作工具：读取、写入、创建、删除文件"
        )

    def get_schema(self) -> Dict[str, Any]:
        """获取 File 工具的 JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "create", "delete", "list"],
                    "description": "文件操作类型"
                },
                "filepath": {
                    "type": "string",
                    "description": "文件路径"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容（写入操作时需要）",
                    "default": ""
                },
                "encoding": {
                    "type": "string",
                    "description": "文件编码",
                    "default": "utf-8"
                }
            },
            "required": ["operation", "filepath"]
        }

    def execute(self, operation: str, filepath: str, content: str = "", encoding: str = "utf-8") -> Dict[str, Any]:
        """
        执行文件操作

        Args:
            operation: 操作类型
            filepath: 文件路径
            content: 文件内容
            encoding: 文件编码

        Returns:
            操作结果
        """
        try:
            import os

            if operation == "read":
                with open(filepath, "r", encoding=encoding) as f:
                    content = f.read()
                return {
                    "success": True,
                    "operation": operation,
                    "filepath": filepath,
                    "content": content
                }

            elif operation == "write":
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding=encoding) as f:
                    f.write(content)
                return {
                    "success": True,
                    "operation": operation,
                    "filepath": filepath
                }

            elif operation == "create":
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding=encoding) as f:
                    f.write(content)
                return {
                    "success": True,
                    "operation": operation,
                    "filepath": filepath
                }

            elif operation == "delete":
                if os.path.exists(filepath):
                    os.remove(filepath)
                    return {
                        "success": True,
                        "operation": operation,
                        "filepath": filepath
                    }
                else:
                    return {
                        "success": False,
                        "error": "文件不存在",
                        "filepath": filepath
                    }

            elif operation == "list":
                if os.path.isdir(filepath):
                    items = os.listdir(filepath)
                    return {
                        "success": True,
                        "operation": operation,
                        "filepath": filepath,
                        "items": sorted(items),
                        "count": len(items)
                    }
                else:
                    return {
                        "success": False,
                        "error": "目录不存在",
                        "filepath": filepath
                    }

            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {operation}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation,
                "filepath": filepath
            }


class SystemTool(MCPTool):
    """系统信息工具"""

    def __init__(self):
        super().__init__(
            name="system",
            description="获取系统信息"
        )

    def get_schema(self) -> Dict[str, Any]:
        """获取 System 工具的 JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "info_type": {
                    "type": "string",
                    "enum": ["platform", "python_version", "environment", "all"],
                    "description": "信息类型",
                    "default": "all"
                }
            },
            "required": ["info_type"]
        }

    def execute(self, info_type: str = "all") -> Dict[str, Any]:
        """
        获取系统信息

        Args:
            info_type: 信息类型

        Returns:
            系统信息
        """
        import platform
        import os
        import sys

        try:
            if info_type == "platform":
                return {
                    "success": True,
                    "info_type": info_type,
                    "data": {
                        "system": platform.system(),
                        "machine": platform.machine(),
                        "processor": platform.processor(),
                        "platform": platform.platform()
                    }
                }

            elif info_type == "python_version":
                return {
                    "success": True,
                    "info_type": info_type,
                    "data": {
                        "version": sys.version,
                        "version_info": {
                            "major": sys.version_info.major,
                            "minor": sys.version_info.minor,
                            "micro": sys.version_info.micro
                        }
                    }
                }

            elif info_type == "environment":
                return {
                    "success": True,
                    "info_type": info_type,
                    "data": {
                        "cwd": os.getcwd(),
                        "env_vars": dict(os.environ)
                    }
                }

            elif info_type == "all":
                return {
                    "success": True,
                    "info_type": info_type,
                    "data": {
                        "platform": {
                            "system": platform.system(),
                            "machine": platform.machine(),
                            "processor": platform.processor(),
                            "platform": platform.platform()
                        },
                        "python_version": {
                            "version": sys.version,
                            "version_info": {
                                "major": sys.version_info.major,
                                "minor": sys.version_info.minor,
                                "micro": sys.version_info.micro
                            }
                        },
                        "environment": {
                            "cwd": os.getcwd(),
                            "env_count": len(os.environ)
                        }
                    }
                }

            else:
                return {
                    "success": False,
                    "error": f"不支持的信息类型: {info_type}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "info_type": info_type
            }


class JSONTool(MCPTool):
    """JSON 处理工具"""

    def __init__(self):
        super().__init__(
            name="json",
            description="JSON 数据处理工具"
        )

    def get_schema(self) -> Dict[str, Any]:
        """获取 JSON 工具的 JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["parse", "stringify", "validate"],
                    "description": "JSON 操作类型"
                },
                "data": {
                    "type": ["string", "object"],
                    "description": "JSON 数据或字符串"
                },
                "indent": {
                    "type": "integer",
                    "description": "缩进空格数",
                    "default": 2
                }
            },
            "required": ["operation", "data"]
        }

    def execute(self, operation: str, data: Any, indent: int = 2) -> Dict[str, Any]:
        """
        执行 JSON 操作

        Args:
            operation: 操作类型
            data: 数据
            indent: 缩进空格数

        Returns:
            操作结果
        """
        try:
            if operation == "parse":
                # 解析 JSON 字符串
                if isinstance(data, str):
                    parsed = json.loads(data)
                    return {
                        "success": True,
                        "operation": operation,
                        "data": parsed
                    }
                else:
                    return {
                        "success": False,
                        "error": "parse 操作需要字符串输入"
                    }

            elif operation == "stringify":
                # 将对象转换为 JSON 字符串
                if isinstance(data, (dict, list)):
                    stringified = json.dumps(data, ensure_ascii=False, indent=indent)
                    return {
                        "success": True,
                        "operation": operation,
                        "data": stringified
                    }
                else:
                    return {
                        "success": False,
                        "error": "stringify 操作需要对象或数组输入"
                    }

            elif operation == "validate":
                # 验证 JSON
                try:
                    if isinstance(data, str):
                        json.loads(data)
                        return {
                            "success": True,
                            "operation": operation,
                            "valid": True
                        }
                    else:
                        return {
                            "success": False,
                            "operation": operation,
                            "error": "validate 操作需要字符串输入"
                        }
                except json.JSONDecodeError as e:
                    return {
                        "success": True,
                        "operation": operation,
                        "valid": False,
                        "error": str(e)
                    }

            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {operation}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }


class NetworkTool(MCPTool):
    """网络操作工具"""

    def __init__(self):
        super().__init__(
            name="network",
            description="网络请求、下载、搜索工具"
        )

    def get_schema(self) -> Dict[str, Any]:
        """获取 Network 工具的 JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["get", "post", "download", "search", "scrape"],
                    "description": "网络操作类型"
                },
                "url": {
                    "type": "string",
                    "description": "URL (search 操作可选)",
                    "default": None
                },
                "params": {
                    "type": "object",
                    "description": "请求参数（GET/POST）"
                },
                "data": {
                    "type": "object",
                    "description": "POST 数据"
                },
                "filepath": {
                    "type": "string",
                    "description": "文件保存路径（download 操作）"
                },
                "query": {
                    "type": "string",
                    "description": "搜索关键词（search 操作）"
                },
                "engine": {
                    "type": "string",
                    "description": "搜索引擎（search 操作）",
                    "default": "duckduckgo"
                },
                "num_results": {
                    "type": "integer",
                    "description": "搜索结果数量（search 操作）",
                    "default": 10
                }
            },
            "required": ["operation"]
        }

    def execute(self, operation: str, url: str = None, **kwargs) -> Dict[str, Any]:
        """
        执行网络操作

        Args:
            operation: 操作类型
            url: URL (search 操作可选)
            **kwargs: 其他参数

        Returns:
            操作结果
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from api import NetworkAPI
            network = NetworkAPI()

            if operation == "get":
                if not url:
                    return {"success": False, "error": "get 操作需要 url 参数"}
                result = network.get(url, params=kwargs.get("params"))
            elif operation == "post":
                if not url:
                    return {"success": False, "error": "post 操作需要 url 参数"}
                result = network.post(url, data=kwargs.get("data"), json_data=kwargs.get("json_data"))
            elif operation == "download":
                if not url:
                    return {"success": False, "error": "download 操作需要 url 参数"}
                filepath = kwargs.get("filepath")
                if not filepath:
                    return {"success": False, "error": "download 操作需要 filepath 参数"}
                result = network.download(url, filepath)
            elif operation == "search":
                query = kwargs.get("query") or url
                if not query:
                    return {"success": False, "error": "search 操作需要 query 参数或 url 参数"}
                result = network.search(query, engine=kwargs.get("engine", "duckduckgo"), num_results=kwargs.get("num_results", 10))
            elif operation == "scrape":
                if not url:
                    return {"success": False, "error": "scrape 操作需要 url 参数"}
                result = network.scrape(url, selector=kwargs.get("selector"))
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {operation}"
                }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }


class DataTool(MCPTool):
    """数据分析工具"""

    def __init__(self):
        super().__init__(
            name="data",
            description="数据分析、统计、过滤工具"
        )

    def get_schema(self) -> Dict[str, Any]:
        """获取 Data 工具的 JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["load_json", "load_csv", "save_json", "analyze", "filter", "group_by", "sort", "summary"],
                    "description": "数据操作类型"
                },
                "filepath": {
                    "type": "string",
                    "description": "文件路径"
                },
                "data": {
                    "type": ["object", "array"],
                    "description": "数据"
                },
                "column": {
                    "type": "string",
                    "description": "列名"
                },
                "condition": {
                    "type": "string",
                    "description": "过滤条件"
                },
                "reverse": {
                    "type": "boolean",
                    "description": "是否降序",
                    "default": False
                }
            },
            "required": ["operation"]
        }

    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        执行数据操作

        Args:
            operation: 操作类型
            **kwargs: 其他参数

        Returns:
            操作结果
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from api import DataAPI
            data_api = DataAPI()

            if operation == "load_json":
                filepath = kwargs.get("filepath")
                if not filepath:
                    return {"success": False, "error": "需要 filepath 参数"}
                result = data_api.load_json(filepath)

            elif operation == "load_csv":
                filepath = kwargs.get("filepath")
                if not filepath:
                    return {"success": False, "error": "需要 filepath 参数"}
                result = data_api.load_csv(filepath, delimiter=kwargs.get("delimiter", ","))

            elif operation == "save_json":
                filepath = kwargs.get("filepath")
                data = kwargs.get("data")
                if not filepath or data is None:
                    return {"success": False, "error": "需要 filepath 和 data 参数"}
                result = data_api.save_json(filepath, data, indent=kwargs.get("indent", 2))

            elif operation == "analyze":
                data = kwargs.get("data")
                column = kwargs.get("column")
                if data is None:
                    return {"success": False, "error": "需要 data 参数"}
                result = data_api.analyze(data, column)

            elif operation == "filter":
                data = kwargs.get("data")
                condition = kwargs.get("condition")
                if data is None or condition is None:
                    return {"success": False, "error": "需要 data 和 condition 参数"}
                result = data_api.filter(data, condition)

            elif operation == "group_by":
                data = kwargs.get("data")
                column = kwargs.get("column")
                if data is None or column is None:
                    return {"success": False, "error": "需要 data 和 column 参数"}
                result = data_api.group_by(data, column)

            elif operation == "sort":
                data = kwargs.get("data")
                column = kwargs.get("column")
                if data is None or column is None:
                    return {"success": False, "error": "需要 data 和 column 参数"}
                result = data_api.sort(data, column, reverse=kwargs.get("reverse", False))

            elif operation == "summary":
                data = kwargs.get("data")
                if data is None:
                    return {"success": False, "error": "需要 data 参数"}
                result = data_api.summary(data)

            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {operation}"
                }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }


class ImageTool(MCPTool):
    """图像处理工具"""

    def __init__(self):
        super().__init__(
            name="image",
            description="图像处理、转换、压缩工具"
        )

    def get_schema(self) -> Dict[str, Any]:
        """获取 Image 工具的 JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["info", "resize", "convert", "compress", "list"],
                    "description": "图像操作类型"
                },
                "filepath": {
                    "type": "string",
                    "description": "图像文件路径"
                },
                "output_path": {
                    "type": "string",
                    "description": "输出文件路径"
                },
                "width": {
                    "type": "integer",
                    "description": "目标宽度"
                },
                "height": {
                    "type": "integer",
                    "description": "目标高度"
                },
                "format": {
                    "type": "string",
                    "description": "目标格式",
                    "default": "JPEG"
                },
                "quality": {
                    "type": "integer",
                    "description": "压缩质量 (1-100)",
                    "default": 85
                },
                "directory": {
                    "type": "string",
                    "description": "目录路径（list 操作）"
                }
            },
            "required": ["operation", "filepath"]
        }

    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        执行图像操作

        Args:
            operation: 操作类型
            **kwargs: 其他参数

        Returns:
            操作结果
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from api import ImageAPI
            image_api = ImageAPI()

            if operation == "info":
                filepath = kwargs.get("filepath")
                result = image_api.info(filepath)

            elif operation == "resize":
                filepath = kwargs.get("filepath")
                output_path = kwargs.get("output_path")
                width = kwargs.get("width")
                height = kwargs.get("height")
                if not all([filepath, output_path, width, height]):
                    return {"success": False, "error": "需要 filepath, output_path, width, height 参数"}
                result = image_api.resize(filepath, output_path, width, height, keep_aspect=kwargs.get("keep_aspect", True))

            elif operation == "convert":
                filepath = kwargs.get("filepath")
                output_path = kwargs.get("output_path")
                format = kwargs.get("format", "JPEG")
                if not all([filepath, output_path]):
                    return {"success": False, "error": "需要 filepath 和 output_path 参数"}
                result = image_api.convert(filepath, output_path, format)

            elif operation == "compress":
                filepath = kwargs.get("filepath")
                output_path = kwargs.get("output_path")
                quality = kwargs.get("quality", 85)
                if not all([filepath, output_path]):
                    return {"success": False, "error": "需要 filepath 和 output_path 参数"}
                result = image_api.compress(filepath, output_path, quality)

            elif operation == "list":
                directory = kwargs.get("directory")
                if not directory:
                    return {"success": False, "error": "需要 directory 参数"}
                result = image_api.list_images(directory, extensions=kwargs.get("extensions"))

            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {operation}"
                }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }


def get_all_tools() -> List[MCPTool]:
    """获取所有可用的 MCP 工具"""
    return [
        ShellTool(),
        FileTool(),
        SystemTool(),
        JSONTool(),
        NetworkTool(),
        DataTool(),
        ImageTool()
    ]