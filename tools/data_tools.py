#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理工具模块
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.memory_agent import BaseTool


class JsonParseTool(BaseTool):
    """JSON 解析工具"""

    def __init__(self):
        super().__init__(
            name="json_parse",
            description="解析JSON字符串。参数: {\"data\": \"JSON字符串\"}"
        )

    def execute(self, data: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(data)
            return {
                "success": True,
                "data": parsed,
                "type": type(parsed).__name__
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON解析错误: {str(e)}"
            }


class JsonStringifyTool(BaseTool):
    """JSON 序列化工具"""

    def __init__(self):
        super().__init__(
            name="json_stringify",
            description="将数据转为JSON字符串。参数: {\"data\": {数据}, \"indent\": 2}"
        )

    def execute(self, data: Any, indent: int = 2) -> Dict[str, Any]:
        try:
            result = json.dumps(data, ensure_ascii=False, indent=indent)
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"序列化错误: {str(e)}"
            }


class DataAnalyzeTool(BaseTool):
    """数据分析工具"""

    def __init__(self):
        super().__init__(
            name="data_analyze",
            description="分析数据列表。参数: {\"data\": [数据列表]}"
        )

    def execute(self, data: List) -> Dict[str, Any]:
        try:
            if not isinstance(data, list):
                return {"success": False, "error": "数据必须是列表"}

            if not data:
                return {"success": True, "data": {"count": 0, "message": "空列表"}}

            # 基本统计
            result = {
                "count": len(data),
                "type": type(data[0]).__name__ if data else None
            }

            # 如果是数值列表
            if all(isinstance(x, (int, float)) for x in data):
                result.update({
                    "sum": sum(data),
                    "min": min(data),
                    "max": max(data),
                    "mean": sum(data) / len(data),
                    "sorted": sorted(data)
                })

            # 如果是字符串列表
            elif all(isinstance(x, str) for x in data):
                result.update({
                    "lengths": [len(s) for s in data],
                    "unique_count": len(set(data))
                })

            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


class DataFilterTool(BaseTool):
    """数据过滤工具"""

    def __init__(self):
        super().__init__(
            name="data_filter",
            description="过滤数据。参数: {\"data\": [列表], \"key\": \"键名\", \"value\": \"值\"}"
        )

    def execute(self, data: List[Dict], key: str, value: Any) -> Dict[str, Any]:
        try:
            if not isinstance(data, list):
                return {"success": False, "error": "数据必须是字典列表"}

            filtered = [item for item in data if item.get(key) == value]
            return {
                "success": True,
                "filtered": filtered,
                "count": len(filtered),
                "original_count": len(data)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class DataSortTool(BaseTool):
    """数据排序工具"""

    def __init__(self):
        super().__init__(
            name="data_sort",
            description="排序数据。参数: {\"data\": [列表], \"key\": \"键名\", \"reverse\": false}"
        )

    def execute(self, data: List, key: str = None, reverse: bool = False) -> Dict[str, Any]:
        try:
            if not isinstance(data, list):
                return {"success": False, "error": "数据必须是列表"}

            if key and all(isinstance(x, dict) for x in data):
                sorted_data = sorted(data, key=lambda x: x.get(key, 0), reverse=reverse)
            else:
                sorted_data = sorted(data, reverse=reverse)

            return {
                "success": True,
                "sorted": sorted_data,
                "count": len(sorted_data)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
