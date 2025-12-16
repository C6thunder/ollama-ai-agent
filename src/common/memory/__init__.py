"""内存管理模块

管理 Agent 的对话历史和上下文
"""

from typing import List, Dict, Any, Optional
import json
import os


class Message:
    """消息类"""

    def __init__(self, role: str, content: str, name: Optional[str] = None, tool_call_id: Optional[str] = None):
        self.role = role
        self.content = content
        self.name = name
        self.tool_call_id = tool_call_id

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "role": self.role,
            "content": self.content,
        }
        if self.name:
            result["name"] = self.name
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建消息"""
        return cls(
            role=data["role"],
            content=data["content"],
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id")
        )


class ConversationMemory:
    """对话内存管理器"""

    def __init__(self, max_messages: int = 100):
        self.max_messages = max_messages
        self.messages: List[Message] = []

    def add_message(self, role: str, content: str, name: Optional[str] = None, tool_call_id: Optional[str] = None):
        """添加消息"""
        message = Message(role, content, name, tool_call_id)
        self.messages.append(message)

        # 如果超过最大消息数，删除最旧的消息
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_messages(self) -> List[Dict[str, Any]]:
        """获取所有消息（字典格式）"""
        return [msg.to_dict() for msg in self.messages]

    def clear(self):
        """清空所有消息"""
        self.messages.clear()

    def save_to_file(self, filepath: str):
        """保存到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(
                [msg.to_dict() for msg in self.messages],
                f,
                indent=2
            )

    def load_from_file(self, filepath: str):
        """从文件加载"""
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.messages = [Message.from_dict(msg) for msg in data]
