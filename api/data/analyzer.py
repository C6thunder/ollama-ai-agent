#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分析模块
"""

import json
from typing import Dict, Any, List, Optional


class DataAnalyzer:
    """数据分析器"""

    def load_json(self, filepath: str) -> Dict[str, Any]:
        """加载 JSON 文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"success": True, "data": data, "filepath": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_csv(self, filepath: str, delimiter: str = ",") -> Dict[str, Any]:
        """加载 CSV 文件"""
        try:
            import csv
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                data = list(reader)
            return {
                "success": True,
                "data": data,
                "count": len(data),
                "columns": list(data[0].keys()) if data else []
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze(self, data: List, column: str = None) -> Dict[str, Any]:
        """分析数据"""
        try:
            if not data:
                return {"success": True, "data": {"count": 0}}

            result = {"count": len(data)}

            # 数值列表
            if all(isinstance(x, (int, float)) for x in data):
                result.update({
                    "sum": sum(data),
                    "min": min(data),
                    "max": max(data),
                    "mean": sum(data) / len(data)
                })

            # 字典列表的特定列
            elif column and all(isinstance(x, dict) for x in data):
                values = [x.get(column) for x in data if column in x]
                if values and all(isinstance(v, (int, float)) for v in values):
                    result.update({
                        "column": column,
                        "sum": sum(values),
                        "min": min(values),
                        "max": max(values),
                        "mean": sum(values) / len(values)
                    })

            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def filter(self, data: List[Dict], key: str, value: Any) -> Dict[str, Any]:
        """过滤数据"""
        try:
            filtered = [item for item in data if item.get(key) == value]
            return {
                "success": True,
                "filtered": filtered,
                "count": len(filtered),
                "original_count": len(data)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sort(self, data: List, key: str = None,
             reverse: bool = False) -> Dict[str, Any]:
        """排序数据"""
        try:
            if key and all(isinstance(x, dict) for x in data):
                sorted_data = sorted(data, key=lambda x: x.get(key, 0), reverse=reverse)
            else:
                sorted_data = sorted(data, reverse=reverse)
            return {"success": True, "sorted": sorted_data, "count": len(sorted_data)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def group_by(self, data: List[Dict], column: str) -> Dict[str, Any]:
        """按列分组"""
        try:
            groups = {}
            for item in data:
                key = item.get(column)
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
            return {
                "success": True,
                "groups": groups,
                "group_count": len(groups)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
