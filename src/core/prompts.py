"""Prompt 模板管理模块

提供统一的 Prompt 模板管理、动态生成和缓存功能
支持多种 Prompt 类型：静态模板、动态模板、上下文感知模板等
"""

import json
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod


class BasePromptTemplate(ABC):
    """Prompt 模板基类"""

    @abstractmethod
    def format(self, **kwargs) -> str:
        """格式化 Prompt"""
        pass

    @abstractmethod
    def get_variables(self) -> List[str]:
        """获取需要的变量"""
        pass


class StaticPromptTemplate(BasePromptTemplate):
    """静态 Prompt 模板"""

    def __init__(self, template: str):
        self.template = template

    def format(self, **kwargs) -> str:
        """格式化 Prompt"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"缺少变量: {e}")

    def get_variables(self) -> List[str]:
        """获取需要的变量"""
        import re
        return re.findall(r'\{(\w+)\}', self.template)


class DynamicPromptTemplate(BasePromptTemplate):
    """动态 Prompt 模板"""

    def __init__(self, template_generator: callable):
        self.template_generator = template_generator

    def format(self, **kwargs) -> str:
        """动态生成 Prompt"""
        return self.template_generator(**kwargs)

    def get_variables(self) -> List[str]:
        """动态获取变量"""
        # 尝试调用生成器获取变量
        try:
            return self.template_generator(variables_only=True)
        except:
            return []


class ContextAwarePromptTemplate(BasePromptTemplate):
    """上下文感知 Prompt 模板"""

    def __init__(
        self,
        base_template: str,
        context_rules: Dict[str, callable]
    ):
        self.base_template = base_template
        self.context_rules = context_rules

    def format(self, **kwargs) -> str:
        """根据上下文格式化 Prompt"""
        # 根据上下文规则调整模板
        template = self.base_template
        context = kwargs.get("context", {})

        for rule_name, rule_func in self.context_rules.items():
            if rule_name in context:
                template = rule_func(template, context[rule_name])

        # 格式化模板
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"缺少变量: {e}")

    def get_variables(self) -> List[str]:
        """获取需要的变量"""
        import re
        return re.findall(r'\{(\w+)\}', self.base_template)


class PromptManager:
    """Prompt 模板管理器"""

    # 预定义的 Prompt 模板
    PROMPTS = {
        # Agent 系统提示
        "system_intro": StaticPromptTemplate(
            """你是一个安全的 AI 助手。

{tool_descriptions}

安全特性:
- 路径限制在项目目录内
- 命令黑名单验证
- 输入长度限制
- 危险字符过滤

工具调用格式：
```json
{{
  "name": "工具名",
  "arguments": {{
    "参数1": "值1",
    "参数2": "值2"
  }}
}}
```"""
        ),

        # 文件操作提示
        "file_operation": StaticPromptTemplate(
            """你是一个文件操作助手。

当前任务: {task_type}
文件路径: {file_path}
操作内容: {operation}

可用工具:
{available_tools}

请根据任务选择合适的工具并返回 JSON 格式的工具调用。"""
        ),

        # 命令执行提示
        "shell_command": StaticPromptTemplate(
            """你是一个安全的 Shell 命令执行器。

黑名单命令: {blacklisted_commands}
危险模式: {dangerous_patterns}
当前目录: {current_dir}

用户命令: {command}

请判断命令是否安全，如果安全请执行，如果危险请拒绝并说明原因。"""
        ),

        # 代码生成提示
        "code_generation": StaticPromptTemplate(
            """你是一个专业的代码生成助手。

编程语言: {language}
任务描述: {task_description}
约束条件: {constraints}
代码风格: {code_style}

请生成高质量的 {language} 代码，要求:
1. 代码规范、注释清晰
2. 遵循 {code_style} 风格
3. 满足所有约束条件
4. 考虑边界情况

代码:"""
        ),

        # 文档分析提示
        "document_analysis": StaticPromptTemplate(
            """你是一个专业的文档分析师。

文档类型: {doc_type}
文档长度: {doc_length}
分析目标: {analysis_goal}

文档内容:
{doc_content}

请根据分析目标 {analysis_goal} 对文档进行分析，提供:
1. 文档摘要
2. 关键信息提取
3. 重要结论
4. 建议行动

分析结果:"""
        ),

        # RAG 问答提示
        "rag_qa": StaticPromptTemplate(
            """你是一个基于文档的问答系统。

问题: {question}

相关文档片段:
{context}

请基于提供的文档内容回答问题。如果文档中没有相关信息，请明确说明。

回答要求:
1. 基于文档内容回答
2. 引用具体文档片段
3. 回答准确、简洁
4. 如果无法回答，说明原因

回答:"""
        ),

        # 代码审查提示
        "code_review": StaticPromptTemplate(
            """你是一个资深的代码审查专家。

代码语言: {language}
审查重点: {review_focus}
代码规范: {coding_standards}

待审查代码:
```{{language}}
{{code}}
```

请从以下角度进行审查:
1. 代码质量
2. 安全性
3. 性能
4. 可维护性
5. 遵循 {coding_standards} 规范

审查意见:"""
        ),

        # 测试生成提示
        "test_generation": StaticPromptTemplate(
            """你是一个测试用例生成专家。

被测代码: {source_code}
测试类型: {test_type}
测试覆盖率: {coverage_requirement}

请生成全面的测试用例，要求:
1. 覆盖 {coverage_requirement} 的代码
2. 包含正常情况和边界情况
3. 测试 {test_type}
4. 使用 {language} 编写

测试代码:"""
        ),

        # 重构建议提示
        "refactor_suggestion": StaticPromptTemplate(
            """你是一个代码重构专家。

原始代码:
```{{language}}
{{source_code}}
```

重构目标: {refactor_goal}
性能要求: {performance_req}
可读性要求: {readability_req}

请提供重构建议和重构后的代码，重构后要求:
1. 提升 {refactor_goal}
2. 满足 {performance_req}
3. 增强 {readability_req}
4. 保持功能不变

重构建议:"""
        ),

        # 错误诊断提示
        "error_diagnosis": StaticPromptTemplate(
            """你是一个专业的错误诊断专家。

错误类型: {error_type}
错误信息: {error_message}
相关代码:
```{{language}}
{{problematic_code}}
```

执行环境: {execution_environment}

请分析错误原因并提供解决方案:
1. 错误原因分析
2. 解决方案
3. 预防措施
4. 最佳实践

诊断结果:"""
        )
    }

    def __init__(self):
        self._templates = self.PROMPTS.copy()
        self._cache = {}  # 简单缓存

    def get_prompt(
        self,
        name: str,
        cache: bool = True,
        **kwargs
    ) -> str:
        """获取 Prompt 模板并格式化

        Args:
            name: 模板名称
            cache: 是否使用缓存
            **kwargs: 模板变量

        Returns:
            格式化后的 Prompt
        """
        # 检查缓存
        cache_key = f"{name}:{json.dumps(kwargs, sort_keys=True)}"
        if cache and cache_key in self._cache:
            return self._cache[cache_key]

        # 获取模板
        if name not in self._templates:
            raise ValueError(f"Prompt 模板 '{name}' 不存在")

        template = self._templates[name]

        # 格式化
        try:
            formatted_prompt = template.format(**kwargs)
        except ValueError as e:
            raise ValueError(f"Prompt 格式化失败: {e}")

        # 缓存
        if cache:
            self._cache[cache_key] = formatted_prompt

        return formatted_prompt

    def register_template(self, name: str, template: BasePromptTemplate):
        """注册新的 Prompt 模板"""
        self._templates[name] = template

    def list_templates(self) -> List[str]:
        """列出所有可用的模板"""
        return list(self._templates.keys())

    def get_template_info(self, name: str) -> Dict[str, Any]:
        """获取模板信息"""
        if name not in self._templates:
            raise ValueError(f"Prompt 模板 '{name}' 不存在")

        template = self._templates[name]
        return {
            "name": name,
            "variables": template.get_variables(),
            "type": type(template).__name__
        }

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()


class PromptTemplateBuilder:
    """Prompt 模板构建器"""

    def __init__(self):
        self.template_parts = []
        self.variables = set()

    def add_text(self, text: str):
        """添加文本"""
        self.template_parts.append(text)
        return self

    def add_variable(self, var_name: str, default: Optional[str] = None):
        """添加变量"""
        if default is not None:
            text = f"{{{var_name}:{default}}}"
        else:
            text = f"{{{var_name}}}"
        self.template_parts.append(text)
        self.variables.add(var_name)
        return self

    def add_section(self, title: str, content: str):
        """添加章节"""
        text = f"\n## {title}\n\n{content}\n"
        self.template_parts.append(text)
        return self

    def build(self) -> StaticPromptTemplate:
        """构建模板"""
        template_str = "".join(self.template_parts)
        return StaticPromptTemplate(template_str)


class PromptEnhancer:
    """Prompt 增强器"""

    @staticmethod
    def add_examples(prompt: str, examples: List[Dict[str, str]]) -> str:
        """添加示例"""
        if not examples:
            return prompt

        example_section = "\n\n示例:\n"
        for i, example in enumerate(examples, 1):
            example_section += f"{i}. 输入: {example['input']}\n"
            example_section += f"   输出: {example['output']}\n"

        return prompt + example_section

    @staticmethod
    def add_constraints(prompt: str, constraints: List[str]) -> str:
        """添加约束"""
        if not constraints:
            return prompt

        constraint_section = "\n\n约束条件:\n"
        for constraint in constraints:
            constraint_section += f"- {constraint}\n"

        return prompt + constraint_section

    @staticmethod
    def add_format_instructions(prompt: str, format_type: str = "json") -> str:
        """添加格式说明"""
        instructions = {
            "json": "请以 JSON 格式返回结果",
            "markdown": "请使用 Markdown 格式返回结果",
            "plain": "请以纯文本格式返回结果"
        }

        if format_type in instructions:
            return prompt + "\n\n" + instructions[format_type]
        return prompt

    @staticmethod
    def add_role_definition(prompt: str, role: str, expertise: str) -> str:
        """添加角色定义"""
        role_def = f"\n\n角色定义:\n你是一个{role}，具有{expertise}。\n"
        return prompt + role_def


# 全局 Prompt 管理器实例
prompt_manager = PromptManager()


def get_prompt_manager() -> PromptManager:
    """获取 Prompt 管理器实例"""
    return prompt_manager


def get_prompt(name: str, **kwargs) -> str:
    """便捷函数：获取 Prompt"""
    return prompt_manager.get_prompt(name, **kwargs)


# 使用示例
if __name__ == "__main__":
    # 1. 使用预定义模板
    prompt = get_prompt(
        "system_intro",
        tool_descriptions="列出所有可用工具..."
    )
    print("系统提示:")
    print(prompt)
    print("\n" + "="*50 + "\n")

    # 2. 使用构建器创建自定义模板
    builder = PromptTemplateBuilder()
    custom_prompt = builder.add_text("你是一个").add_variable("role").add_text("专家。") \
        .add_section("任务", "请执行以下任务:").add_variable("task") \
        .build()
    print("自定义模板:")
    print(custom_prompt.format(role="代码审查", task="审查 Python 代码"))
    print("\n" + "="*50 + "\n")

    # 3. 使用增强器
    enhanced = PromptEnhancer.add_role_definition(
        "请分析这段代码",
        "资深开发者",
        "10年 Python 开发经验"
    )
    print("增强后的 Prompt:")
    print(enhanced)
