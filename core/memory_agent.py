#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain Agent with Memory
带记忆的智能代理，独立的实现
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod

from .memory import MemoryManager


class BaseTool(ABC):
    """工具基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具操作"""
        pass


class MemoryReActAgent:
    """
    带记忆的智能代理
    独立的 ReAct Agent 实现，不依赖老代码
    """

    def __init__(
        self,
        llm_client,
        tools: Dict[str, BaseTool],
        memory_manager: MemoryManager,
        max_iterations: int = 10,
        verbose: bool = True,
        current_time: Optional[Dict[str, Any]] = None
    ):
        """
        初始化带记忆的智能代理

        Args:
            llm_client: LLM 客户端
            tools: 工具字典
            memory_manager: 记忆管理器
            max_iterations: 最大迭代次数
            verbose: 是否显示详细输出
            current_time: 当前时间信息
        """
        self.llm = llm_client
        self.tools = tools
        self.memory_manager = memory_manager
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.current_time = current_time
        self.history: List[Dict[str, str]] = []

    def _build_prompt(self, task: str, scratchpad: str = "") -> str:
        """
        构建 ReAct 提示词

        Args:
            task: 用户任务描述
            scratchpad: 当前思考过程

        Returns:
            完整的提示词
        """
        # 获取记忆上下文
        memory_context = self.memory_manager.get_context_for_agent()

        # 构建工具描述
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools.values()
        ])

        # 构建当前时间信息
        current_time_context = ""
        if self.current_time:
            dt = self.current_time.get('datetime', 'N/A')
            ts = self.current_time.get('timestamp', 'N/A')
            current_time_context = f"\n## 当前时间信息\n系统当前时间: {dt}\n时间戳: {ts}\n\n"

        # 构建提示词
        prompt = f"""你是一个智能AI代理，使用ReAct(Reasoning and Acting)框架解决问题。

{memory_context}

{current_time_context}## 可用工具
{tools_desc}

## 参数格式要求
- 所有工具参数必须以 JSON 格式提供
- 即使无参数也必须写 {{}}
- 字符串值使用双引号

## 响应格式 - 严格遵循
你必须按以下格式之一回应：

**格式1 - 调用工具:**
Thought: 你必须先写一个思考过程
Action: 工具名称
Action Input: JSON格式参数

**格式2 - 直接回答:**
Thought: 你必须先写一个思考过程
Final Answer: 给用户的最终回答

## 重要规则
1. **必须包含Thought**: 每次回应都必须以 "Thought: " 开头，这是必需的
2. **简单问候处理**: 如果用户只是问候（如"你好"、"hi"、"hello"），直接给出Final Answer回应问候，无需使用工具
3. 每次只执行一个Action
4. 分析Observation后再决定下一步
5. 遇到错误时修改参数或换工具
6. 完成后给出Final Answer
7. **禁止编造**: 只能使用工具返回的真实数据，绝对不能伪造搜索结果或链接

## 当前任务
{task}

{scratchpad}"""

        return prompt

    def _parse_response(self, response: str) -> Tuple[str, Optional[str], Optional[Dict], Optional[str]]:
        """
        解析 LLM 响应

        Returns:
            (thought, action, action_input, final_answer)
        """
        thought = ""
        action = None
        action_input = None
        final_answer = None

        # 提取 Thought
        thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|Final Answer:|$)', response, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()

        # 检查是否有 Final Answer
        final_match = re.search(r'Final Answer:\s*(.+?)$', response, re.DOTALL)
        if final_match:
            final_answer = final_match.group(1).strip()
            return thought, None, None, final_answer

        # 提取 Action
        action_match = re.search(r'Action:\s*(.+)', response)
        if action_match:
            action = action_match.group(1).strip()

        # 提取 Action Input
        input_match = re.search(r'Action Input:\s*(.+?)(?=Thought:|Action:|Observation:|$)', response, re.DOTALL)
        if input_match:
            input_str = input_match.group(1).strip()
            try:
                action_input = json.loads(input_str)
            except json.JSONDecodeError:
                action_input = {"input": input_str}

        return thought, action, action_input, final_answer

    def _execute_tool(self, action: str, action_input: Dict) -> str:
        """
        执行工具（带记忆记录）

        Args:
            action: 工具名称
            action_input: 工具输入参数

        Returns:
            工具执行结果
        """
        if action not in self.tools:
            return f"错误: 未知工具 '{action}'。可用工具: {list(self.tools.keys())}"

        tool = self.tools[action]
        try:
            result = tool.execute(**action_input)
            if isinstance(result, dict):
                return json.dumps(result, ensure_ascii=False, indent=2)
            return str(result)
        except Exception as e:
            return f"工具执行错误: {str(e)}"

    def run(self, task: str) -> str:
        """
        执行 ReAct 循环

        Args:
            task: 用户任务描述

        Returns:
            最终答案
        """
        # 记录用户输入
        self.memory_manager.add_user_input(task)

        scratchpad = ""

        for i in range(self.max_iterations):
            if self.verbose:
                print(f"\n{'='*50}")
                print(f"迭代 {i + 1}/{self.max_iterations}")
                print('='*50)

            # 构建提示词并调用 LLM
            prompt = self._build_prompt(task, scratchpad)
            response = self.llm(prompt)

            if self.verbose:
                print(f"\n[LLM 响应]\n{response}")

            # 解析响应
            thought, action, action_input, final_answer = self._parse_response(response)

            if self.verbose and thought:
                print(f"\n[Thought] {thought}")

            # 如果有最终答案，返回
            if final_answer:
                if self.verbose:
                    print(f"\n[Final Answer] {final_answer}")
                self._record_history(task, final_answer)
                self.memory_manager.add_assistant_response(final_answer)
                self.memory_manager.save_session()
                return final_answer

            # 执行工具
            if action is not None and action_input is not None:
                if self.verbose:
                    print(f"\n[Action] {action}")
                    print(f"[Action Input] {json.dumps(action_input, ensure_ascii=False)}")

                observation = self._execute_tool(action, action_input)

                if self.verbose:
                    print(f"\n[Observation]\n{observation}")

                # 记录工具执行
                self.memory_manager.add_tool_execution(action, json.dumps(action_input, ensure_ascii=False), observation)

                # 更新 scratchpad
                scratchpad += f"\nThought: {thought}\nAction: {action}\nAction Input: {json.dumps(action_input, ensure_ascii=False)}\nObservation: {observation}\n"
            else:
                # 如果没有有效的 action，记录并继续
                scratchpad += f"\nThought: {thought}\n"

        # 达到最大迭代次数
        return "达到最大迭代次数，任务未完成。"

    def _record_history(self, task: str, answer: str):
        """记录历史"""
        self.history.append({
            "task": task,
            "answer": answer
        })

    def get_history(self) -> List[Dict[str, str]]:
        """获取历史记录"""
        return self.history

    def clear_history(self):
        """清空历史"""
        self.history.clear()

    def get_memory_summary(self) -> str:
        """
        获取记忆摘要

        Returns:
            格式化的记忆摘要
        """
        stats = self.memory_manager.get_stats()
        recent = self.memory_manager.conversation_memory.get_recent(5)

        summary = f"""
## 记忆摘要

会话ID: {stats['session_id']}
对话条目: {stats['total_entries']}
长期记忆: {stats['long_term_count']}
会话时长: {stats['session_duration']:.1f} 秒

## 最近对话
"""

        for entry in recent:
            summary += f"- [{entry.type}] {entry.content[:100]}...\n"

        return summary

    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索记忆

        Args:
            query: 搜索关键词

        Returns:
            搜索结果列表
        """
        results = self.memory_manager.search_memory(query)
        return [
            {
                'id': entry.id,
                'type': entry.type,
                'content': entry.content,
                'importance': entry.importance,
                'timestamp': entry.timestamp
            }
            for entry in results
        ]

    def clear_memory(self):
        """清空对话记忆"""
        self.memory_manager.clear_conversation_memory()


class MemoryAwareAgentBuilder:
    """
    记忆感知 Agent 构建器
    """

    @staticmethod
    def create_agent(
        llm_client,
        base_tools: Dict[str, Any],
        memory_tools: Dict[str, Any],
        session_id: Optional[str] = None,
        **kwargs
    ) -> MemoryReActAgent:
        """
        创建带记忆的 Agent

        Args:
            llm_client: LLM 客户端
            base_tools: 基础工具字典
            memory_tools: 记忆工具字典
            session_id: 会话ID
            **kwargs: 其他参数

        Returns:
            MemoryReActAgent 实例
        """
        # 合并工具
        all_tools = {**base_tools, **memory_tools}

        # 创建记忆管理器
        memory_manager = MemoryManager(session_id=session_id)

        # 创建 Agent
        agent = MemoryReActAgent(
            llm_client=llm_client,
            tools=all_tools,
            memory_manager=memory_manager,
            **kwargs
        )

        return agent
