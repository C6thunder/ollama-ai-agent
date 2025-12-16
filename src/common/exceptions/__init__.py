"""项目自定义异常

定义项目中使用的各种自定义异常类型
"""


class AgentError(Exception):
    """基础异常类"""
    pass


class SecurityError(AgentError):
    """安全相关错误"""
    pass


class ValidationError(AgentError):
    """验证错误"""
    pass


class ConfigurationError(AgentError):
    """配置错误"""
    pass


class ToolExecutionError(AgentError):
    """工具执行错误"""
    pass


class DocumentLoadError(AgentError):
    """文档加载错误"""
    pass


class VectorStoreError(AgentError):
    """向量存储错误"""
    pass


class ChainExecutionError(AgentError):
    """链执行错误"""
    pass


class PromptError(AgentError):
    """Prompt 错误"""
    pass


class OutputParseError(AgentError):
    """输出解析错误"""
    pass
