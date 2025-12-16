"""安全验证模块

提供输入验证、路径验证、命令验证等功能
支持从配置文件读取安全参数
"""

import os
import re
import json
from typing import Dict, Any, Tuple, List, Optional
from pathlib import Path


class SecurityConfig:
    """安全配置管理器"""

    _config = None

    @classmethod
    def load_config(cls, config_path: str = "config/config.json"):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._config = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config: {e}")
            cls._config = {}

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if cls._config is None:
            cls.load_config()

        keys = key.split('.')
        value = cls._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """获取安全配置"""
        return cls.get("security", {})

    @classmethod
    def get_tools_config(cls) -> Dict[str, Any]:
        """获取工具配置"""
        return cls.get("tools", {})


class SecurityValidator:
    """安全验证器（基于配置）"""

    @classmethod
    def _get_allowed_base_dir(cls) -> str:
        """获取允许的基础目录"""
        base_dir = SecurityConfig.get("security.base_directory", os.path.dirname(__file__))
        return os.path.realpath(base_dir)

    @classmethod
    def _get_allowed_directories(cls) -> List[str]:
        """获取允许的目录列表"""
        dirs = SecurityConfig.get("security.allowed_directories", [])
        return [os.path.realpath(d) for d in dirs]

    @classmethod
    def _get_blocked_directories(cls) -> List[str]:
        """获取禁止的目录列表"""
        dirs = SecurityConfig.get("security.blocked_directories", [])
        return [os.path.realpath(d) for d in dirs]

    @classmethod
    def _get_allowed_commands(cls) -> Dict[str, List[str]]:
        """获取允许的命令列表"""
        return SecurityConfig.get("security.allowed_commands", {})

    @classmethod
    def _get_blocked_commands(cls) -> List[str]:
        """获取禁止的命令列表"""
        return SecurityConfig.get("security.blocked_commands", [])

    @classmethod
    def _get_dangerous_patterns(cls) -> List[str]:
        """获取危险模式列表"""
        return SecurityConfig.get("security.dangerous_patterns", [])

    @classmethod
    def _get_max_input_length(cls) -> int:
        """获取最大输入长度"""
        return SecurityConfig.get("security.max_input_length", 1000)

    @classmethod
    def _get_max_output_size(cls) -> int:
        """获取最大输出大小"""
        return SecurityConfig.get("security.max_output_size", 5000)

    @classmethod
    def _get_max_file_size(cls) -> int:
        """获取最大文件大小"""
        return SecurityConfig.get("tools.file.max_file_size", 100000)

    @classmethod
    def _get_max_read_size(cls) -> int:
        """获取最大读取大小"""
        return SecurityConfig.get("tools.file.max_read_size", 10000)

    @classmethod
    def _get_command_timeout(cls) -> int:
        """获取命令超时时间"""
        return SecurityConfig.get("tools.shell.command_timeout", 10)

    @classmethod
    def _get_allowed_chars(cls) -> str:
        """获取允许的字符集"""
        return SecurityConfig.get("security.allowed_chars",
                                  "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_./: ")

    @classmethod
    def _get_blocked_chars(cls) -> List[str]:
        """获取禁止的字符列表（移除!，因为它是特殊命令前缀）"""
        return SecurityConfig.get("security.blocked_chars",
                                  [";", "|", "&", "`", "$", "(", ")", "<", ">", "\\", "'", "\"", "*", "?", "[", "]", "{", "}"])

    @classmethod
    def _is_path_traversal_check_enabled(cls) -> bool:
        """检查是否启用路径遍历检查"""
        return SecurityConfig.get("security.path_traversal_check", True)

    @classmethod
    def _is_symlink_check_enabled(cls) -> bool:
        """检查是否启用符号链接检查"""
        return SecurityConfig.get("security.symlink_check", True)

    @classmethod
    def _is_file_sanitization_enabled(cls) -> bool:
        """检查是否启用文件清理"""
        return SecurityConfig.get("security.file_sanitization", True)

    @classmethod
    def _is_command_whitelist_mode(cls) -> bool:
        """检查是否使用命令白名单模式"""
        return SecurityConfig.get("security.command_whitelist_mode", True)

    @classmethod
    def _is_directory_whitelist_mode(cls) -> bool:
        """检查是否使用目录白名单模式"""
        return SecurityConfig.get("security.directory_whitelist_mode", True)

    @classmethod
    def _should_log_security_events(cls) -> bool:
        """检查是否记录安全事件"""
        return SecurityConfig.get("security.log_security_events", True)

    @classmethod
    def validate_path(cls, path: str, check_write: bool = False) -> Tuple[bool, str]:
        """验证文件路径是否安全

        Args:
            path: 文件路径
            check_write: 是否检查写权限

        Returns:
            Tuple[bool, str]: (是否安全, 错误信息)
        """
        # 规范化路径
        try:
            real_path = os.path.realpath(path)
            base_path = os.path.realpath(cls._get_allowed_base_dir())

            # 检查是否在允许目录内
            allowed_dirs = cls._get_allowed_directories()
            blocked_dirs = cls._get_blocked_directories()

            # 首先检查是否在禁止目录内
            for blocked_dir in blocked_dirs:
                if real_path.startswith(blocked_dir + os.sep) or real_path == blocked_dir:
                    return False, f"路径在禁止目录内: {path}"

            # 检查目录白名单模式
            if cls._is_directory_whitelist_mode():
                is_allowed = False
                for allowed_dir in allowed_dirs:
                    if real_path.startswith(allowed_dir + os.sep) or real_path == allowed_dir:
                        is_allowed = True
                        break

                if not is_allowed:
                    return False, f"路径不在允许目录内: {path}"
            else:
                # 黑名单模式：检查是否在基础目录内
                if not (real_path.startswith(base_path + os.sep) or real_path == base_path):
                    return False, f"路径不在允许目录内: {path}"

            # 检查路径遍历
            if cls._is_path_traversal_check_enabled():
                if '..' in path:
                    return False, f"不允许路径遍历: {path}"

            # 检查符号链接
            if cls._is_symlink_check_enabled():
                if os.path.islink(path):
                    return False, f"不允许符号链接: {path}"

            # 检查写权限（如果需要）
            if check_write:
                parent_dir = os.path.dirname(real_path)
                if not os.access(parent_dir, os.W_OK):
                    return False, f"没有写权限: {parent_dir}"

            return True, "安全"

        except Exception as e:
            return False, f"路径验证错误: {str(e)}"

    @classmethod
    def validate_shell_command(cls, cmd: str) -> Tuple[bool, str]:
        """验证 Shell 命令是否安全

        Args:
            cmd: Shell 命令

        Returns:
            Tuple[bool, str]: (是否安全, 错误信息)
        """
        # 检查是否为空
        if not cmd or not cmd.strip():
            return False, "命令不能为空"

        # 检查长度
        max_length = SecurityConfig.get("security.max_input_length", 1000)
        if len(cmd) > max_length:
            return False, f"命令过长 (最大 {max_length} 字符)"

        # 检查危险模式
        dangerous_patterns = cls._get_dangerous_patterns()
        for pattern in dangerous_patterns:
            if re.search(pattern, cmd, re.IGNORECASE):
                return False, f"命令包含危险模式: {pattern}"

        # 检查禁止的字符
        blocked_chars = cls._get_blocked_chars()
        for char in blocked_chars:
            if char in cmd:
                return False, f"命令包含危险字符: {char}"

        # 检查命令白名单
        parts = cmd.split()
        if not parts:
            return False, "无效命令"

        command = parts[0]

        # 检查是否在禁止列表中
        blocked_commands = cls._get_blocked_commands()
        if command in blocked_commands:
            return False, f"命令在禁止列表中: {command}"

        # 检查白名单模式
        if cls._is_command_whitelist_mode():
            allowed_commands = cls._get_allowed_commands()
            if command not in allowed_commands:
                return False, f"命令不在允许列表中: {command}"

            # 检查参数
            if len(parts) > 1:
                args = parts[1:]
                allowed_args = allowed_commands.get(command, [])

                # 如果有允许的参数列表，检查参数
                if allowed_args:
                    for arg in args:
                        # 跳过文件名等动态参数
                        if arg.startswith('-'):
                            if arg not in allowed_args:
                                return False, f"不允许的参数: {arg}"

        return True, "安全"

    @classmethod
    def validate_tool_call(cls, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """验证工具调用 JSON 是否安全

        Args:
            content: 包含 JSON 的文本

        Returns:
            Tuple[bool, str, Dict]: (是否安全, 错误信息, 工具调用字典)
        """
        try:
            # 提取 JSON
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if not json_match:
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)

            if not json_match:
                return False, "未找到 JSON", {}

            json_str = json_match.group(1)

            # 解析 JSON
            try:
                tool_call = json.loads(json_str)
            except json.JSONDecodeError as e:
                return False, f"JSON 格式错误: {str(e)}", {}

            # 验证工具名
            tool_name = tool_call.get("name")
            if not tool_name:
                return False, "工具名不能为空", {}

            # 检查工具名是否在允许列表中
            allowed_tools = [
                "write_file_tool",
                "read_file_tool",
                "delete_file_tool",
                "list_files_tool",
                "shell_command_tool",
                "get_working_directory_tool"
            ]
            if tool_name not in allowed_tools:
                return False, f"不允许的工具: {tool_name}", {}

            # 验证参数
            arguments = tool_call.get("arguments", {})
            if not isinstance(arguments, dict):
                return False, "参数必须是字典", {}

            # 特定工具的验证
            if tool_name == "write_file_tool":
                path = arguments.get("path", "")
                is_safe, error = cls.validate_path(path, check_write=True)
                if not is_safe:
                    return False, f"文件路径不安全: {error}", {}

                content = arguments.get("content", "")
                max_file_size = cls._get_max_file_size()
                if len(content) > max_file_size:
                    return False, f"文件内容过大 (最大 {max_file_size} 字节)", {}

            elif tool_name == "read_file_tool":
                path = arguments.get("path", "")
                is_safe, error = cls.validate_path(path, check_write=False)
                if not is_safe:
                    return False, f"文件路径不安全: {error}", {}

            elif tool_name == "shell_command_tool":
                cmd = arguments.get("cmd", "")
                is_safe, error = cls.validate_shell_command(cmd)
                if not is_safe:
                    return False, f"命令不安全: {error}", {}

            elif tool_name == "list_files_tool":
                directory = arguments.get("directory", ".")
                is_safe, error = cls.validate_path(directory, check_write=False)
                if not is_safe:
                    return False, f"目录路径不安全: {error}", {}

            elif tool_name == "delete_file_tool":
                path = arguments.get("path", "")
                is_safe, error = cls.validate_path(path, check_write=True)
                if not is_safe:
                    return False, f"文件路径不安全: {error}", {}

            elif tool_name == "get_working_directory_tool":
                # 这个工具不需要参数验证
                pass

            return True, "安全", tool_call

        except Exception as e:
            return False, f"验证错误: {str(e)}", {}

    @classmethod
    def validate_user_input(cls, user_input: str) -> Tuple[bool, str]:
        """验证用户输入

        Args:
            user_input: 用户输入

        Returns:
            Tuple[bool, str]: (是否安全, 错误信息)
        """
        # 长度检查
        max_length = cls._get_max_input_length()
        if len(user_input) > max_length:
            return False, f"输入过长 (最大 {max_length} 字符)"

        # 检查空输入
        if not user_input.strip():
            return False, "输入不能为空"

        # 特殊命令检查 - 以!开头的命令是允许的
        if user_input.strip().startswith("!"):
            # 特殊命令只需要检查长度和危险模式，不需要检查危险字符
            dangerous_patterns = cls._get_dangerous_patterns()
            for pattern in dangerous_patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    return False, f"输入包含危险模式: {pattern}"
            return True, "安全"

        # 检查危险模式（这是主要的验证）
        dangerous_patterns = cls._get_dangerous_patterns()
        for pattern in dangerous_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False, f"输入包含危险模式: {pattern}"

        # 只检查非常危险的字符（不检查常见字符如括号、方括号等）
        extremely_dangerous_chars = ["`", "$", "\\", "<", ">"]
        for char in extremely_dangerous_chars:
            if char in user_input:
                return False, f"输入包含危险字符: {char}"

        return True, "安全"

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """清理文件名

        Args:
            filename: 文件名

        Returns:
            str: 清理后的文件名
        """
        # 检查是否启用清理
        if not cls._is_file_sanitization_enabled():
            return filename

        # 移除危险字符
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # 限制长度
        if len(sanitized) > 255:
            sanitized = sanitized[:255]

        # 移除前后空格和点
        sanitized = sanitized.strip(' .')

        return sanitized

    @classmethod
    def limit_output_size(cls, output: str) -> str:
        """限制输出大小

        Args:
            output: 输出内容

        Returns:
            str: 限制后的输出
        """
        max_size = cls._get_max_output_size()
        if len(output) > max_size:
            return output[:max_size] + "\n... (输出过长，已截断)"
        return output

    @classmethod
    def limit_file_list(cls, files: List[str]) -> List[str]:
        """限制文件列表大小

        Args:
            files: 文件列表

        Returns:
            List[str]: 限制后的文件列表
        """
        max_files = SecurityConfig.get("security.max_files_list", 100)
        if len(files) > max_files:
            return files[:max_files]
        return files
