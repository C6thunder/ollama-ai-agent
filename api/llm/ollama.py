#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama LLM 客户端
"""

import requests
from typing import Dict, Any, List, Optional


class OllamaAPI:
    """Ollama API 客户端"""

    def __init__(self, model: str = "qwen2.5:7b",
                 host: str = "127.0.0.1", port: int = 11434):
        self.model = model
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"

    def is_available(self) -> bool:
        """检查服务是否可用"""
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[Dict]:
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            return response.json().get("models", [])
        except:
            return []

    def generate(self, prompt: str, stream: bool = False,
                 temperature: float = 0.7, max_tokens: int = None) -> Dict[str, Any]:
        """生成文本"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "temperature": temperature
        }
        if max_tokens:
            data["max_tokens"] = max_tokens

        try:
            response = requests.post(
                f"{self.base_url}/v1/completions",
                json=data,
                timeout=120
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def chat(self, messages: List[Dict[str, str]],
             temperature: float = 0.7) -> Dict[str, Any]:
        """聊天补全"""
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": temperature
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=data,
                timeout=120
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def __call__(self, prompt: str) -> str:
        """简单调用接口"""
        response = self.generate(prompt)
        if "error" in response:
            return response["error"]
        choices = response.get("choices", [])
        if choices:
            return choices[0].get("text", "")
        return "无法获取回复"


# 向后兼容别名
OllamaClient = OllamaAPI
