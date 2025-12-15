#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆模块
实现短期记忆（会话内）和长期记忆（持久化）
"""

import os
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
from collections import defaultdict, Counter


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

        # 语义索引 - 关键词到记忆条目ID的映射
        self.semantic_index: Dict[str, Set[str]] = defaultdict(set)

        # 停用词列表（常见的无意义词汇）
        self.stop_words = {
            '的', '了', '是', '在', '我', '你', '他', '她', '它',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'that',
            'this', 'these', 'those', 'it', 'its', 'be', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could'
        }

    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        从文本中提取关键词

        Args:
            text: 输入文本
            max_keywords: 最大关键词数量

        Returns:
            关键词列表
        """
        # 转换为小写并提取单词
        text = text.lower()

        # 使用正则提取单词（包含中文字符、英文单词）
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)

        # 过滤停用词和短词
        keywords = [
            word for word in words
            if word not in self.stop_words and len(word) >= 2
        ]

        # 统计词频并取前N个
        word_freq = Counter(keywords)
        top_keywords = [word for word, _ in word_freq.most_common(max_keywords)]

        return top_keywords

    def _update_semantic_index(self, entry: MemoryEntry):
        """
        更新语义索引

        Args:
            entry: 记忆条目
        """
        # 提取关键词
        keywords = self._extract_keywords(entry.content)

        # 将条目ID添加到关键词索引中
        for keyword in keywords:
            self.semantic_index[keyword].add(entry.id)

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

        # 更新语义索引
        self._update_semantic_index(entry)

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

    def semantic_search(self, query: str, limit: int = 10) -> List[Tuple[MemoryEntry, float]]:
        """
        语义搜索记忆

        Args:
            query: 查询关键词
            limit: 返回结果数量限制

        Returns:
            (记忆条目, 匹配分数) 的列表，按分数降序排列
        """
        # 提取查询关键词
        query_keywords = self._extract_keywords(query, max_keywords=5)

        if not query_keywords:
            return []

        # 查找匹配的记忆条目ID
        matched_ids: Set[str] = set()
        keyword_scores: Dict[str, int] = defaultdict(int)

        for keyword in query_keywords:
            # 计算关键词权重（基于长度和频率）
            weight = len(keyword) + 1

            if keyword in self.semantic_index:
                matched_ids.update(self.semantic_index[keyword])
                keyword_scores[keyword] = weight

        # 计算每个记忆条目的匹配分数
        entry_scores: Dict[str, float] = defaultdict(float)
        for mem_id in matched_ids:
            # 查找对应的记忆条目
            for entry in self.entries:
                if entry.id == mem_id:
                    # 计算匹配分数：基于关键词权重和条目重要性
                    entry_keywords = self._extract_keywords(entry.content, max_keywords=20)
                    match_score = sum(keyword_scores.get(kw, 0) for kw in entry_keywords if kw in query_keywords)
                    final_score = match_score * entry.importance
                    entry_scores[mem_id] = final_score
                    break

        # 按分数排序并返回
        sorted_results = sorted(
            [(self._get_entry_by_id(mem_id), score) for mem_id, score in entry_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )

        # 过滤掉分数为0的结果
        filtered_results = [(entry, score) for entry, score in sorted_results if score > 0]

        return filtered_results[:limit]

    def _get_entry_by_id(self, mem_id: str) -> Optional[MemoryEntry]:
        """
        根据ID获取记忆条目

        Args:
            mem_id: 记忆条目ID

        Returns:
            记忆条目或None
        """
        for entry in self.entries:
            if entry.id == mem_id:
                return entry
        return None

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
        """搜索记忆（简单关键词匹配）"""
        # 搜索对话记忆
        conversation_matches = self.conversation_memory.search(query)

        # 搜索长期记忆
        long_term_matches = self.persistent_memory.search_long_term(query)

        # 合并并去重
        all_matches = conversation_matches + long_term_matches

        # 按重要性排序
        all_matches.sort(key=lambda x: x.importance, reverse=True)

        return all_matches

    def semantic_search_memory(self, query: str, limit: int = 10) -> List[Tuple[MemoryEntry, float]]:
        """
        语义搜索记忆

        Args:
            query: 查询关键词
            limit: 返回结果数量限制

        Returns:
            (记忆条目, 匹配分数) 的列表，按分数降序排列
        """
        # 语义搜索对话记忆
        conversation_results = self.conversation_memory.semantic_search(query, limit=limit)

        # 对长期记忆也进行简单关键词搜索（可以进一步优化为语义搜索）
        long_term_matches = self.persistent_memory.search_long_term(query, limit=limit)

        # 合并结果
        combined_results: Dict[str, Tuple[MemoryEntry, float]] = {}

        # 添加对话记忆结果
        for entry, score in conversation_results:
            combined_results[entry.id] = (entry, score)

        # 添加长期记忆结果（赋予较低的基础分数）
        for entry in long_term_matches:
            if entry.id not in combined_results:
                combined_results[entry.id] = (entry, entry.importance * 5.0)

        # 转换为列表并按分数排序
        all_results = list(combined_results.values())
        all_results.sort(key=lambda x: x[1], reverse=True)

        return all_results[:limit]

    def get_related_memories(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """
        获取相关记忆（语义搜索的简化接口）

        Args:
            query: 查询关键词
            limit: 返回结果数量限制

        Returns:
            相关记忆条目列表
        """
        results = self.semantic_search_memory(query, limit)
        return [entry for entry, _ in results]

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
