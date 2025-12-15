#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain Ollama LLM 适配器
将现有的 OllamaAPI 适配为 LangChain LLM
"""

from typing import Dict, Any, List, Optional, Iterator, Union
from langchain_core.language_models import BaseLanguageModel
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult, Generation
from pydantic import BaseModel, Field
import requests
import json


class LangChainOllamaLLM(BaseLanguageModel):
    """
    LangChain Ollama LLM 适配器

    包装现有的 OllamaAPI，使其符合 LangChain LLM 接口
    """

    model: str = Field(default="qwen2.5:7b", description="模型名称")
    host: str = Field(default="127.0.0.1", description="Ollama 主机地址")
    port: int = Field(default=11434, description="Ollama 端口")
    temperature: float = Field(default=0.7, description="采样温度")
    max_tokens: Optional[int] = Field(default=None, description="最大生成 token 数")

    class Config:
        """Pydantic 配置"""
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        """标识 LLM 类型"""
        return "ollama"

    @property
    def _base_url(self) -> str:
        """获取基础 URL"""
        return f"http://{self.host}:{self.port}"

    def _generate_prompt(self, prompts: List[str], stop: Optional[List[str]] = None) -> List[str]:
        """生成提示词"""
        return prompts

    async def agenerate_prompt(self, prompts: List[str], stop: Optional[List[str]] = None) -> List[str]:
        """异步生成提示词"""
        return self._generate_prompt(prompts, stop)

    def generate_prompt(self, prompts: List[str], stop: Optional[List[str]] = None) -> List[str]:
        """生成提示词"""
        return self._generate_prompt(prompts, stop)

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        调用 LLM 生成文本

        Args:
            prompt: 输入提示词
            stop: 停止词列表
            run_manager: 回调管理器
            **kwargs: 额外参数

        Returns:
            生成的文本
        """
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": self.temperature
        }

        if self.max_tokens:
            data["max_tokens"] = self.max_tokens

        if stop:
            data["stop"] = stop

        try:
            response = requests.post(
                f"{self._base_url}/v1/completions",
                json=data,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                return f"错误: {result['error']}"

            choices = result.get("choices", [])
            if choices:
                return choices[0].get("text", "")

            return "无法获取回复"

        except Exception as e:
            return f"调用失败: {str(e)}"

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """
        流式调用 LLM

        Args:
            prompt: 输入提示词
            stop: 停止词列表
            run_manager: 回调管理器
            **kwargs: 额外参数

        Yields:
            生成的文本片段
        """
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "temperature": self.temperature
        }

        if self.max_tokens:
            data["max_tokens"] = self.max_tokens

        if stop:
            data["stop"] = stop

        try:
            with requests.post(
                f"{self._base_url}/v1/completions",
                json=data,
                stream=True,
                timeout=120
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]  # 移除 "data: " 前缀
                            if data_str == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data_str)
                                choices = chunk.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    text = delta.get("text", "")
                                    if text:
                                        yield text
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            yield f"流式调用失败: {str(e)}"

    def invoke(
        self,
        input: Union[str, List[Dict[str, str]]],
        config: Optional[Any] = None,
        **kwargs: Any,
    ) -> Union[str, LLMResult]:
        """
        同步调用 LLM（LangChain v0.1+ 接口）

        Args:
            input: 输入（字符串或消息列表）
            config: 配置
            **kwargs: 额外参数

        Returns:
            生成的文本或 LLMResult
        """
        if isinstance(input, list):
            # 如果是消息列表，转换为字符串
            prompt = self._format_messages(input)
        else:
            prompt = input

        text = self._call(prompt, **kwargs)
        return text

    async def ainvoke(
        self,
        input: Union[str, List[Dict[str, str]]],
        config: Optional[Any] = None,
        **kwargs: Any,
    ) -> Union[str, LLMResult]:
        """
        异步调用 LLM

        Args:
            input: 输入（字符串或消息列表）
            config: 配置
            **kwargs: 额外参数

        Returns:
            生成的文本或 LLMResult
        """
        # 对于同步适配器，这里调用同步版本
        # 在实际项目中，可以使用 aiohttp 实现真正的异步
        result = self.invoke(input, config, **kwargs)
        return result

    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        格式化消息列表为提示词

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]

        Returns:
            格式化的提示词
        """
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                formatted.append(f"系统: {content}")
            elif role == "user":
                formatted.append(f"用户: {content}")
            elif role == "assistant":
                formatted.append(f"助手: {content}")

        return "\n".join(formatted)

    def get_available_models(self) -> List[Dict]:
        """
        获取可用的模型列表

        Returns:
            模型列表
        """
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=10)
            return response.json().get("models", [])
        except:
            return []

    def is_available(self) -> bool:
        """
        检查服务是否可用

        Returns:
            是否可用
        """
        try:
            response = requests.get(self._base_url, timeout=5)
            return response.status_code == 200
        except:
            return False


# 向后兼容别名
OllamaLLM = LangChainOllamaLLM
