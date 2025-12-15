#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆工具模块
提供记忆查询、管理和检索功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_agent import BaseTool
from core.memory import MemoryManager, MemoryEntry


class MemorySearchTool(BaseTool):
    """记忆搜索工具"""

    def __init__(self, memory_manager: MemoryManager):
        super().__init__(
            name="memory_search",
            description="搜索记忆库中的相关信息。参数: {\"query\": \"搜索关键词\", \"limit\": 5}"
        )
        self.memory_manager = memory_manager

    def execute(self, query: str, limit: int = 5) -> dict:
        """搜索记忆"""
        try:
            results = self.memory_manager.search_memory(query)
            results = results[:limit]

            formatted_results = []
            for entry in results:
                formatted_results.append({
                    'id': entry.id,
                    'type': entry.type,
                    'content': entry.content[:200] + '...' if len(entry.content) > 200 else entry.content,
                    'importance': entry.importance,
                    'timestamp': entry.timestamp
                })

            return {
                'success': True,
                'query': query,
                'count': len(formatted_results),
                'results': formatted_results
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class MemoryListTool(BaseTool):
    """列出所有记忆工具"""

    def __init__(self, memory_manager: MemoryManager):
        super().__init__(
            name="memory_list",
            description="列出所有记忆条目。无需参数。"
        )
        self.memory_manager = memory_manager

    def execute(self) -> dict:
        """列出记忆"""
        try:
            entries = self.memory_manager.conversation_memory.entries
            formatted = []

            for entry in entries:
                formatted.append({
                    'id': entry.id,
                    'type': entry.type,
                    'content_preview': entry.content[:100],
                    'importance': entry.importance,
                    'timestamp': entry.timestamp
                })

            stats = self.memory_manager.get_stats()

            return {
                'success': True,
                'total_entries': len(entries),
                'stats': stats,
                'entries': formatted
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class MemoryContextTool(BaseTool):
    """获取记忆上下文工具"""

    def __init__(self, memory_manager: MemoryManager):
        super().__init__(
            name="memory_context",
            description="获取当前对话的上下文记忆。参数: {\"limit\": 20}"
        )
        self.memory_manager = memory_manager

    def execute(self, limit: int = 20) -> dict:
        """获取上下文"""
        try:
            context = self.memory_manager.get_context_for_agent()

            return {
                'success': True,
                'context': context,
                'entry_count': len(self.memory_manager.conversation_memory.entries)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class MemoryClearTool(BaseTool):
    """清空记忆工具"""

    def __init__(self, memory_manager: MemoryManager):
        super().__init__(
            name="memory_clear",
            description="清空对话记忆（保留长期记忆）。无需参数。"
        )
        self.memory_manager = memory_manager

    def execute(self) -> dict:
        """清空记忆"""
        try:
            self.memory_manager.clear_conversation_memory()
            return {
                'success': True,
                'message': '对话记忆已清空，长期记忆已保留'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class MemoryStatsTool(BaseTool):
    """记忆统计工具"""

    def __init__(self, memory_manager: MemoryManager):
        super().__init__(
            name="memory_stats",
            description="获取记忆使用统计。无需参数。"
        )
        self.memory_manager = memory_manager

    def execute(self) -> dict:
        """获取统计"""
        try:
            stats = self.memory_manager.get_stats()
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


def get_memory_tools(memory_manager: MemoryManager) -> dict:
    """
    获取记忆工具字典

    Args:
        memory_manager: 记忆管理器实例

    Returns:
        工具字典
    """
    tools = [
        MemorySearchTool(memory_manager),
        MemoryListTool(memory_manager),
        MemoryContextTool(memory_manager),
        MemoryClearTool(memory_manager),
        MemoryStatsTool(memory_manager),
    ]

    return {tool.name: tool for tool in tools}
