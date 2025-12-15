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
3. **优先直接操作**: 如果用户要求创建文件、读取文件、列出目录等，直接使用对应工具执行，不要先搜索
4. **搜索仅用于未知信息**: 仅当需要获取外部信息（如实时数据、特定知识）时才使用搜索工具
5. 每次只执行一个Action
6. 分析Observation后再决定下一步
7. 遇到错误时修改参数或换工具
8. 完成后给出Final Answer
9. **禁止编造**: 只能使用工具返回的真实数据，绝对不能伪造搜索结果或链接

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
                # 处理 LLM 错误地将参数包装在 input 字段中的情况
                if isinstance(action_input, dict) and len(action_input) == 1 and "input" in action_input:
                    try:
                        # 尝试解析嵌套的 JSON 字符串
                        nested_input = json.loads(action_input["input"])
                        action_input = nested_input
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败，保持原样
                        pass
            except json.JSONDecodeError:
                action_input = {"input": input_str}

        return thought, action, action_input, final_answer

    def _classify_error(self, error_msg: str) -> Dict[str, Any]:
        """
        分类和诊断错误

        Args:
            error_msg: 错误信息

        Returns:
            错误分析结果，包含错误类型、原因和建议
        """
        error_info = {
            "type": "unknown",
            "severity": "medium",
            "cause": "",
            "suggestion": ""
        }

        error_lower = error_msg.lower()

        # 参数错误
        if "unexpected keyword argument" in error_lower or "参数" in error_lower:
            error_info["type"] = "parameter_error"
            error_info["severity"] = "high"
            error_info["cause"] = "工具参数格式不正确或参数名错误"
            error_info["suggestion"] = "检查工具参数格式，确保参数名和类型正确"

        # 工具不存在
        elif "未知工具" in error_lower or "unknown tool" in error_lower:
            error_info["type"] = "unknown_tool"
            error_info["severity"] = "high"
            error_info["cause"] = "调用的工具不存在"
            error_info["suggestion"] = "使用正确的工具名称，可用的工具有: " + ", ".join(self.tools.keys())

        # 文件相关错误
        elif "文件不存在" in error_lower or "not exist" in error_lower:
            error_info["type"] = "file_not_found"
            error_info["severity"] = "medium"
            error_info["cause"] = "指定的文件或目录不存在"
            error_info["suggestion"] = "检查文件路径是否正确，或先创建文件"

        # 权限错误
        elif "权限" in error_lower or "permission" in error_lower:
            error_info["type"] = "permission_error"
            error_info["severity"] = "high"
            error_info["cause"] = "没有执行该操作的权限"
            error_info["suggestion"] = "检查文件权限或使用其他路径"

        # 网络错误
        elif "网络" in error_lower or "network" in error_lower or "连接" in error_lower:
            error_info["type"] = "network_error"
            error_info["severity"] = "medium"
            error_info["cause"] = "网络连接问题"
            error_info["suggestion"] = "检查网络连接或稍后重试"

        # 执行超时
        elif "超时" in error_lower or "timeout" in error_lower:
            error_info["type"] = "timeout"
            error_info["severity"] = "medium"
            error_info["cause"] = "操作执行超时"
            error_info["suggestion"] = "简化操作或检查系统状态"

        # 通用错误
        else:
            error_info["type"] = "execution_error"
            error_info["severity"] = "medium"
            error_info["cause"] = "工具执行过程中发生错误"
            error_info["suggestion"] = "检查输入参数和系统状态"

        return error_info

    def _generate_correction(self, action: str, action_input: Dict, error_info: Dict[str, Any]) -> Optional[Dict]:
        """
        生成错误纠正建议

        Args:
            action: 工具名称
            action_input: 原始输入参数
            error_info: 错误分析结果

        Returns:
            纠正后的参数或None（如果无法自动纠正）
        """
        error_type = error_info["type"]

        # 参数错误的自动纠正
        if error_type == "parameter_error":
            # 检查是否是 input 字段嵌套问题
            if isinstance(action_input, dict) and "input" in action_input:
                input_value = action_input["input"]

                # 如果 input 字段的值已经是字典，直接返回
                if isinstance(input_value, dict):
                    return input_value

                # 如果是字符串，尝试解析JSON
                try:
                    nested = json.loads(input_value)
                    if isinstance(nested, dict):
                        return nested
                except (json.JSONDecodeError, TypeError):
                    pass

            # 尝试修正常见的参数名错误
            tool = self.tools.get(action)
            if tool:
                # 获取工具的描述信息
                desc = tool.description

                # 简单的参数名匹配纠正（这里可以扩展更复杂的逻辑）
                if "filepath" in desc and "file" in str(action_input):
                    # 如果描述中提到filepath但参数中只有file，尝试转换
                    if "file" in action_input and "filepath" not in action_input:
                        new_input = action_input.copy()
                        new_input["filepath"] = new_input.pop("file")
                        return new_input

        # 文件不存在错误 - 建议检查路径
        elif error_type == "file_not_found":
            # 可以建议列出目录或创建文件
            return {"suggestion": "check_or_create", "original_params": action_input}

        return None

    def _handle_tool_error(self, action: str, action_input: Dict, error_msg: str, iteration: int) -> Tuple[str, Optional[str], Optional[Dict], str]:
        """
        处理工具执行错误，尝试自我纠正

        Args:
            action: 工具名称
            action_input: 工具输入参数
            error_msg: 错误信息
            iteration: 当前迭代次数

        Returns:
            (thought, action, action_input, observation)
        """
        # 分类错误
        error_info = self._classify_error(error_msg)

        # 构建反思提示词
        reflection_prompt = f"""工具执行失败分析：
错误类型: {error_info['type']}
严重程度: {error_info['severity']}
错误原因: {error_info['cause']}
建议解决方案: {error_info['suggestion']}

原始输入:
- 工具: {action}
- 参数: {json.dumps(action_input, ensure_ascii=False)}

请基于错误分析，提出解决方案：
1. 如果是参数错误，提供正确的参数格式
2. 如果是工具不存在，选择合适的替代工具
3. 如果是文件问题，建议先创建文件或检查路径
4. 如果是其他问题，提供替代方案

请严格按照以下格式回复：
Thought: 分析错误原因和解决方案
Action: 工具名称（如果需要）
Action Input: JSON格式参数（如果需要）
"""

        # 调用LLM获取纠正建议
        response = self.llm(reflection_prompt)

        # 解析LLM响应
        thought, new_action, new_action_input, final_answer = self._parse_response(response)

        # 如果LLM返回了Final Answer，说明它认为问题已经解决，
        # 但实际上我们还没有重新执行工具，所以我们需要使用纠正后的参数
        if final_answer and not new_action:
            # LLM没有提供新的action，返回原始action和自动纠正的参数
            correction = self._generate_correction(action, action_input, error_info)
            if correction:
                return f"检测到参数错误，已自动纠正", action, correction, f"错误已纠正: {error_info['type']}"

        # 如果LLM提供了新的参数，使用纠正后的参数
        if new_action_input and new_action_input == action_input:
            # 参数没有变化，尝试自动纠正
            correction = self._generate_correction(action, action_input, error_info)
            if correction:
                return thought, action, correction, f"错误已纠正: {error_info['type']}"

        return thought, new_action, new_action_input, f"错误已纠正: {error_info['type']}"

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

            # 执行工具（带错误处理）
            if action is not None and action_input is not None:
                if self.verbose:
                    print(f"\n[Action] {action}")
                    print(f"[Action Input] {json.dumps(action_input, ensure_ascii=False)}")

                observation = self._execute_tool(action, action_input)

                if self.verbose:
                    print(f"\n[Observation]\n{observation}")

                # 检查是否出现错误
                is_error = (
                    observation.startswith("错误:") or
                    observation.startswith("工具执行错误:") or
                    "unexpected keyword argument" in observation.lower()
                )

                if is_error:
                    # 尝试自我纠正
                    if self.verbose:
                        print(f"\n[错误检测] 检测到错误，尝试自我纠正...")

                    # 分类错误并尝试自动纠正
                    error_info = self._classify_error(observation)
                    correction = self._generate_correction(action, action_input, error_info)

                    correction_thought, correction_action, correction_action_input, correction_obs = self._handle_tool_error(
                        action, action_input, observation, i
                    )

                    # 使用纠正后的参数重新执行
                    should_retry = False

                    # 检查LLM是否提供了纠正
                    if correction_action or correction_action_input:
                        # LLM提供了新的action或参数
                        if correction_action != action or correction_action_input != action_input:
                            should_retry = True
                            final_action = correction_action or action
                            final_input = correction_action_input or action_input
                        else:
                            final_action = action
                            final_input = action_input
                    else:
                        # LLM没有提供纠正，但可能有自动纠正
                        if correction and isinstance(correction, dict):
                            should_retry = True
                            final_action = action
                            final_input = correction
                        else:
                            final_action = None
                            final_input = None

                    if should_retry and final_action and final_input:
                        if self.verbose:
                            print(f"\n[自我纠正] 使用纠正后的参数重新执行")
                            print(f"  原始Action: {action}, 纠正后Action: {final_action}")
                            print(f"  原始参数: {json.dumps(action_input, ensure_ascii=False)}")
                            print(f"  纠正后参数: {json.dumps(final_input, ensure_ascii=False)}")

                        # 重新执行
                        observation = self._execute_tool(final_action, final_input)

                        if self.verbose:
                            print(f"\n[纠正后 Observation]\n{observation}")

                        # 记录纠正后的工具执行
                        self.memory_manager.add_tool_execution(
                            final_action,
                            json.dumps(final_input, ensure_ascii=False),
                            observation
                        )

                        # 更新 scratchpad
                        scratchpad += f"\nThought: {thought}\nAction: {action}\nAction Input: {json.dumps(action_input, ensure_ascii=False)}\nObservation: {observation}\n[自我纠正] {correction_thought}\n纠正后Action: {final_action}\n纠正后Action Input: {json.dumps(final_input, ensure_ascii=False)}\n纠正后Observation: {observation}\n"
                    else:
                        # 无法纠正，记录错误
                        self.memory_manager.add_tool_execution(action, json.dumps(action_input, ensure_ascii=False), observation)
                        scratchpad += f"\nThought: {thought}\nAction: {action}\nAction Input: {json.dumps(action_input, ensure_ascii=False)}\nObservation: {observation}\n[错误] 无法自动纠正\n"
                else:
                    # 正常执行，记录工具执行
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
