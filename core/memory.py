#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆模块
实现短期记忆（会话内）和长期记忆（持久化）
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    timestamp: float
    type: str  # 'user', 'assistant', 'tool', 'result', 'summary'
    content: str
    metadata: Dict[str, Any]
    importance: float = 0.5  # 重要性评分 0-1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        return cls(**data)


class ConversationMemory:
    """对话记忆 - 短期记忆，存储在内存中"""

    def __init__(self, max_entries: int = 100):
        """
        初始化对话记忆

        Args:
            max_entries: 最大记忆条目数
        """
        self.max_entries = max_entries
        self.entries: List[MemoryEntry] = []
        self.session_start = time.time()

    def add(
        self,
        content: str,
        mem_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
    ) -> str:
        """
        添加记忆条目

        Args:
            content: 记忆内容
            mem_type: 记忆类型
            metadata: 元数据
            importance: 重要性 (0-1)

        Returns:
            记忆条目ID
        """
        # 生成唯一ID
        timestamp = time.time()
        unique_str = f"{timestamp}{content}{len(self.entries)}"
        mem_id = hashlib.md5(unique_str.encode()).hexdigest()[:12]

        entry = MemoryEntry(
            id=mem_id,
            timestamp=timestamp,
            type=mem_type,
            content=content,
            metadata=metadata or {},
            importance=importance,
        )

        self.entries.append(entry)

        # 保持大小限制
        if len(self.entries) > self.max_entries:
            # 删除重要性最低的条目
            self.entries.sort(key=lambda x: x.importance)
            self.entries = self.entries[-self.max_entries:]

        return mem_id

    def add_user_input(self, user_input: str) -> str:
        """添加用户输入"""
        return self.add(user_input, 'user', importance=0.8)

    def add_assistant_response(self, response: str) -> str:
        """添加助手回复"""
        return self.add(response, 'assistant', importance=0.7)

    def add_tool_execution(self, tool_name: str, input_data: str, output: str) -> str:
        """添加工具执行记录"""
        content = f"工具: {tool_name}\n输入: {input_data}\n输出: {output}"
        metadata = {
            'tool': tool_name,
            'input': input_data,
            'output_preview': output[:100] if len(output) > 100 else output
        }
        return self.add(content, 'tool', metadata=metadata, importance=0.6)

    def add_summary(self, summary: str) -> str:
        """添加总结"""
        return self.add(summary, 'summary', importance=0.9)

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """获取最近的记忆"""
        return self.entries[-n:] if n < len(self.entries) else self.entries

    def get_by_type(self, mem_type: str) -> List[MemoryEntry]:
        """按类型获取记忆"""
        return [e for e in self.entries if e.type == mem_type]

    def search(self, query: str) -> List[MemoryEntry]:
        """搜索记忆（简单关键词匹配）"""
        query = query.lower()
        return [
            e for e in self.entries
            if query in e.content.lower()
        ]

    def get_context(self, limit: int = 20) -> str:
        """
        获取对话上下文

        Args:
            limit: 最大条目数

        Returns:
            格式化的上下文字符串
        """
        recent = self.get_recent(limit)
        context = "## 对话历史\n\n"

        for entry in recent:
            timestamp = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S")
            if entry.type == 'user':
                context += f"[{timestamp}] 用户: {entry.content}\n"
            elif entry.type == 'assistant':
                context += f"[{timestamp}] 助手: {entry.content}\n"
            elif entry.type == 'tool':
                context += f"[{timestamp}] 工具执行: {entry.metadata.get('tool', 'unknown')}\n"

        return context

    def clear(self):
        """清空记忆"""
        self.entries.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计"""
        type_counts = {}
        for entry in self.entries:
            type_counts[entry.type] = type_counts.get(entry.type, 0) + 1

        return {
            'total_entries': len(self.entries),
            'session_duration': time.time() - self.session_start,
            'type_counts': type_counts,
            'avg_importance': sum(e.importance for e in self.entries) / len(self.entries) if self.entries else 0
        }


class PersistentMemory:
    """持久化记忆 - 长期记忆，存储在文件中"""

    def __init__(self, storage_dir: str = "memory"):
        """
        初始化持久化记忆

        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        # 长期记忆文件
        self.long_term_file = self.storage_dir / "long_term.json"
        self.sessions_dir = self.storage_dir / "sessions"

        self.sessions_dir.mkdir(exist_ok=True)

        # 加载长期记忆
        self.long_term_entries: List[MemoryEntry] = self._load_long_term()

    def _load_long_term(self) -> List[MemoryEntry]:
        """加载长期记忆"""
        if self.long_term_file.exists():
            try:
                with open(self.long_term_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [MemoryEntry.from_dict(item) for item in data]
            except Exception as e:
                print(f"加载长期记忆失败: {e}")
        return []

    def _save_long_term(self):
        """保存长期记忆"""
        try:
            data = [entry.to_dict() for entry in self.long_term_entries]
            with open(self.long_term_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存长期记忆失败: {e}")

    def store_important(self, content: str, importance: float = 0.8) -> str:
        """
        存储重要记忆

        Args:
            content: 记忆内容
            importance: 重要性 (0-1)，只有 >= 0.8 才会长期保存

        Returns:
            记忆条目ID
        """
        if importance < 0.8:
            return ""  # 不保存低重要性记忆

        timestamp = time.time()
        unique_str = f"{timestamp}{content}"
        mem_id = hashlib.md5(unique_str.encode()).hexdigest()[:12]

        entry = MemoryEntry(
            id=mem_id,
            timestamp=timestamp,
            type='persistent',
            content=content,
            metadata={},
            importance=importance,
        )

        self.long_term_entries.append(entry)
        self._save_long_term()

        return mem_id

    def search_long_term(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """
        搜索长期记忆

        Args:
            query: 搜索关键词
            limit: 返回数量限制

        Returns:
            匹配的记忆条目
        """
        query = query.lower()
        matches = [
            e for e in self.long_term_entries
            if query in e.content.lower()
        ]

        # 按重要性排序
        matches.sort(key=lambda x: x.importance, reverse=True)

        return matches[:limit]

    def get_related_memories(self, keyword: str) -> List[MemoryEntry]:
        """获取相关记忆"""
        return self.search_long_term(keyword)

    def save_session(self, session_id: str, conversation_memory: ConversationMemory):
        """
        保存会话

        Args:
            session_id: 会话ID
            conversation_memory: 对话记忆
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        try:
            data = {
                'session_id': session_id,
                'timestamp': time.time(),
                'entries': [entry.to_dict() for entry in conversation_memory.entries],
                'stats': conversation_memory.get_stats()
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存会话失败: {e}")

    def load_session(self, session_id: str) -> Optional[List[MemoryEntry]]:
        """
        加载会话

        Args:
            session_id: 会话ID

        Returns:
            会话记忆条目列表
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [MemoryEntry.from_dict(item) for item in data.get('entries', [])]
        except Exception as e:
            print(f"加载会话失败: {e}")
            return None

    def list_sessions(self) -> List[str]:
        """列出所有会话"""
        return [f.stem for f in self.sessions_dir.glob("*.json")]


class MemoryManager:
    """记忆管理器 - 统一管理短期和长期记忆"""

    def __init__(self, session_id: Optional[str] = None, max_conversation_entries: int = 100):
        """
        初始化记忆管理器

        Args:
            session_id: 会话ID
            max_conversation_entries: 对话记忆最大条目数
        """
        self.session_id = session_id or f"session_{int(time.time())}"
        self.conversation_memory = ConversationMemory(max_entries=max_conversation_entries)
        self.persistent_memory = PersistentMemory()

        # 加载历史会话
        self._load_session()

    def _load_session(self):
        """加载会话记忆"""
        historical = self.persistent_memory.load_session(self.session_id)
        if historical:
            self.conversation_memory.entries.extend(historical)

    def add_user_input(self, user_input: str) -> str:
        """添加用户输入"""
        mem_id = self.conversation_memory.add_user_input(user_input)
        return mem_id

    def add_assistant_response(self, response: str) -> str:
        """添加助手回复"""
        mem_id = self.conversation_memory.add_assistant_response(response)

        # 重要回复保存到长期记忆
        if len(response) > 50:  # 较长的回复才保存
            self.persistent_memory.store_important(
                f"用户提问后，助手回复: {response[:200]}...",
                importance=0.7
            )

        return mem_id

    def add_tool_execution(self, tool_name: str, input_data: str, output: str) -> str:
        """添加工具执行"""
        return self.conversation_memory.add_tool_execution(tool_name, input_data, output)

    def add_summary(self, summary: str) -> str:
        """添加总结"""
        mem_id = self.conversation_memory.add_summary(summary)

        # 重要总结保存到长期记忆
        self.persistent_memory.store_important(summary, importance=0.9)

        return mem_id

    def get_context_for_agent(self) -> str:
        """
        为 Agent 获取格式化上下文

        Returns:
            包含对话历史的上下文字符串
        """
        context = self.conversation_memory.get_context(limit=15)

        # 添加相关长期记忆
        context += "\n\n## 相关历史信息\n"
        recent_user = self.conversation_memory.get_recent(1)
        if recent_user:
            latest_query = recent_user[0].content
            # 搜索相关长期记忆
            keywords = latest_query.split()[:3]  # 取前3个关键词
            related = []
            for keyword in keywords:
                related.extend(self.persistent_memory.get_related_memories(keyword))

            if related:
                for entry in related[:3]:  # 最多3条
                    context += f"- {entry.content}\n"

        return context

    def search_memory(self, query: str) -> List[MemoryEntry]:
        """搜索记忆"""
        # 搜索对话记忆
        conversation_matches = self.conversation_memory.search(query)

        # 搜索长期记忆
        long_term_matches = self.persistent_memory.search_long_term(query)

        # 合并并去重
        all_matches = conversation_matches + long_term_matches

        # 按重要性排序
        all_matches.sort(key=lambda x: x.importance, reverse=True)

        return all_matches

    def save_session(self):
        """保存当前会话"""
        self.persistent_memory.save_session(self.session_id, self.conversation_memory)

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计"""
        stats = self.conversation_memory.get_stats()
        stats['long_term_count'] = len(self.persistent_memory.long_term_entries)
        stats['session_id'] = self.session_id
        return stats

    def clear_conversation_memory(self):
        """清空对话记忆"""
        self.conversation_memory.clear()

    def list_all_memories(self) -> str:
        """列出所有记忆"""
        stats = self.get_stats()
        output = f"""
## 记忆统计

会话ID: {stats['session_id']}
对话条目: {stats['total_entries']}
长期记忆: {stats['long_term_count']}
会话时长: {stats['session_duration']:.1f} 秒

## 对话历史

"""

        for entry in self.conversation_memory.entries:
            timestamp = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S")
            output += f"[{timestamp}] [{entry.type}] {entry.content}\n"

        return output
