"""输出解析器模块

解析 LLM 输出为结构化数据
支持多种输出格式：JSON、XML、CSV、表格、自定义格式等

主要功能：
1. JSON 解析
2. 工具调用解析
3. 结构化数据解析
4. 表格数据解析
5. 自定义格式解析
"""

import json
import re
import csv
from io import StringIO
from typing import Any, Dict, List, Optional, Type, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParsedOutput:
    """解析结果"""

    data: Any
    format: str
    confidence: float
    raw_output: str
    metadata: Dict[str, Any]


class BaseOutputParser(ABC):
    """输出解析器基类"""

    @abstractmethod
    def parse(self, output: str) -> ParsedOutput:
        """解析输出"""
        pass

    @abstractmethod
    def get_format_instructions(self) -> str:
        """获取格式说明"""
        pass


class JSONOutputParser(BaseOutputParser):
    """JSON 输出解析器"""

    def __init__(self, strict: bool = True):
        self.strict = strict

    def parse(self, output: str) -> ParsedOutput:
        """解析 JSON 输出"""
        try:
            # 提取 JSON
            json_str = self._extract_json(output)
            if not json_str:
                raise ValueError("未找到 JSON 数据")

            # 解析 JSON
            data = json.loads(json_str)

            return ParsedOutput(
                data=data,
                format="json",
                confidence=1.0,
                raw_output=output,
                metadata={"parser": "json", "strict": self.strict}
            )

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {str(e)}")
            return ParsedOutput(
                data=None,
                format="json",
                confidence=0.0,
                raw_output=output,
                metadata={"error": str(e), "parser": "json"}
            )

    def _extract_json(self, output: str) -> Optional[str]:
        """提取 JSON 字符串"""
        # 尝试从代码块中提取
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output, re.DOTALL)
        if json_match:
            return json_match.group(1)

        # 尝试直接提取
        json_match = re.search(r'(\{.*\})', output, re.DOTALL)
        if json_match:
            return json_match.group(1)

        return None

    def get_format_instructions(self) -> str:
        """获取格式说明"""
        return "请以 JSON 格式返回结果"


class ToolCallParser(BaseOutputParser):
    """工具调用解析器"""

    def __init__(self):
        self.required_fields = ["name", "arguments"]

    def parse(self, output: str) -> ParsedOutput:
        """解析工具调用"""
        try:
            # 提取工具调用
            tool_call = self._extract_tool_call(output)
            if not tool_call:
                raise ValueError("未找到工具调用")

            # 验证必需字段
            for field in self.required_fields:
                if field not in tool_call:
                    raise ValueError(f"缺少必需字段: {field}")

            return ParsedOutput(
                data=tool_call,
                format="tool_call",
                confidence=1.0,
                raw_output=output,
                metadata={"parser": "tool_call"}
            )

        except Exception as e:
            logger.error(f"工具调用解析失败: {str(e)}")
            return ParsedOutput(
                data=None,
                format="tool_call",
                confidence=0.0,
                raw_output=output,
                metadata={"error": str(e), "parser": "tool_call"}
            )

    def _extract_tool_call(self, output: str) -> Optional[Dict[str, Any]]:
        """提取工具调用"""
        # 尝试 JSON 格式
        json_match = re.search(r'```(?:json)?\s*(\{.*?"name".*?"arguments".*?\})\s*```', output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # 尝试直接 JSON
        json_match = re.search(r'(\{.*?"name".*?"arguments".*?\})', output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # 尝试结构化文本格式
        return self._extract_structured_text(output)

    def _extract_structured_text(self, output: str) -> Optional[Dict[str, Any]]:
        """从结构化文本中提取"""
        # 查找工具名
        name_match = re.search(r'工具\s*名\s*[:：]\s*(\w+)', output)
        if not name_match:
            return None
        name = name_match.group(1)

        # 查找参数
        args = {}
        arg_matches = re.finditer(r'(\w+)\s*[:：]\s*([^\n,]+)', output)
        for match in arg_matches:
            key, value = match.groups()
            if key != "name":  # 跳过工具名
                # 尝试解析 JSON 类型的值
                try:
                    # 去除引号并解析
                    value = value.strip().strip('"\'')
                    if value.startswith('[') or value.startswith('{'):
                        args[key] = json.loads(value)
                    else:
                        args[key] = value
                except:
                    args[key] = value.strip().strip('"\'')

        return {"name": name, "arguments": args}

    def get_format_instructions(self) -> str:
        """获取格式说明"""
        return """请以以下 JSON 格式返回：
{
  "name": "工具名",
  "arguments": {
    "参数1": "值1",
    "参数2": "值2"
  }
}"""


class CSVOutputParser(BaseOutputParser):
    """CSV 输出解析器"""

    def parse(self, output: str) -> ParsedOutput:
        """解析 CSV 输出"""
        try:
            # 提取 CSV
            csv_str = self._extract_csv(output)
            if not csv_str:
                raise ValueError("未找到 CSV 数据")

            # 解析 CSV
            reader = csv.DictReader(StringIO(csv_str))
            data = list(reader)

            return ParsedOutput(
                data=data,
                format="csv",
                confidence=1.0,
                raw_output=output,
                metadata={"parser": "csv", "row_count": len(data)}
            )

        except Exception as e:
            logger.error(f"CSV 解析失败: {str(e)}")
            return ParsedOutput(
                data=None,
                format="csv",
                confidence=0.0,
                raw_output=output,
                metadata={"error": str(e), "parser": "csv"}
            )

    def _extract_csv(self, output: str) -> Optional[str]:
        """提取 CSV 字符串"""
        # 查找 CSV 代码块
        csv_match = re.search(r'```(?:csv)?\s*(\S.*?)\s*```', output, re.DOTALL)
        if csv_match:
            return csv_match.group(1)

        # 查找表格
        lines = output.split('\n')
        csv_lines = []
        in_table = False

        for line in lines:
            line = line.strip()
            # 检测表格开始
            if '|' in line or ',' in line:
                in_table = True
                csv_lines.append(line)
            elif in_table and line == '':
                break

        if csv_lines:
            return '\n'.join(csv_lines)

        return None

    def get_format_instructions(self) -> str:
        """获取格式说明"""
        return "请以 CSV 格式返回数据（使用逗号分隔）"


class StructuredOutputParser(BaseOutputParser):
    """结构化输出解析器"""

    def __init__(self, schema: Dict[str, Type]):
        self.schema = schema

    def parse(self, output: str) -> ParsedOutput:
        """解析结构化输出"""
        try:
            # 提取结构化数据
            data = self._extract_structured_data(output)

            # 验证类型
            validated_data = self._validate_types(data)

            return ParsedOutput(
                data=validated_data,
                format="structured",
                confidence=0.9,
                raw_output=output,
                metadata={"parser": "structured", "schema": self.schema}
            )

        except Exception as e:
            logger.error(f"结构化数据解析失败: {str(e)}")
            return ParsedOutput(
                data=None,
                format="structured",
                confidence=0.0,
                raw_output=output,
                metadata={"error": str(e), "parser": "structured"}
            )

    def _extract_structured_data(self, output: str) -> Dict[str, Any]:
        """从输出中提取结构化数据"""
        data = {}

        # 尝试 JSON 格式
        try:
            json_str = self._extract_json(output)
            if json_str:
                return json.loads(json_str)
        except:
            pass

        # 尝试从文本中提取字段
        for field, field_type in self.schema.items():
            # 查找字段值
            patterns = [
                rf'{field}\s*[:：]\s*([^\n]+)',
                rf'{field}\s*=\s*([^\n]+)',
                rf'{field}\s+([^\n]+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()

                    # 类型转换
                    if field_type == int:
                        value = int(value)
                    elif field_type == float:
                        value = float(value)
                    elif field_type == bool:
                        value = value.lower() in ('true', 'yes', '1', '是', '对')
                    elif field_type == list:
                        # 尝试解析列表
                        if value.startswith('[') and value.endswith(']'):
                            value = json.loads(value)
                        else:
                            value = [item.strip() for item in value.split(',')]

                    data[field] = value
                    break

        return data

    def _extract_json(self, output: str) -> Optional[str]:
        """提取 JSON"""
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output, re.DOTALL)
        if json_match:
            return json_match.group(1)
        return None

    def _validate_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证数据类型"""
        validated = {}
        for field, expected_type in self.schema.items():
            if field in data:
                value = data[field]
                if isinstance(value, expected_type):
                    validated[field] = value
                else:
                    logger.warning(f"字段 {field} 类型不匹配: 期望 {expected_type}, 得到 {type(value)}")
                    validated[field] = value
            else:
                logger.warning(f"缺少字段: {field}")

        return validated

    def get_format_instructions(self) -> str:
        """获取格式说明"""
        schema_str = json.dumps(self.schema, indent=2)
        return f"请以 JSON 格式返回数据，字段类型定义如下：\n{schema_str}"


class ListOutputParser(BaseOutputParser):
    """列表输出解析器"""

    def __init__(self, item_type: Type = str):
        self.item_type = item_type

    def parse(self, output: str) -> ParsedOutput:
        """解析列表输出"""
        try:
            # 提取列表
            items = self._extract_list(output)

            # 类型转换
            converted_items = []
            for item in items:
                try:
                    if self.item_type == int:
                        converted_items.append(int(item))
                    elif self.item_type == float:
                        converted_items.append(float(item))
                    else:
                        converted_items.append(str(item).strip())
                except:
                    converted_items.append(str(item).strip())

            return ParsedOutput(
                data=converted_items,
                format="list",
                confidence=0.9,
                raw_output=output,
                metadata={"parser": "list", "item_type": self.item_type.__name__}
            )

        except Exception as e:
            logger.error(f"列表解析失败: {str(e)}")
            return ParsedOutput(
                data=None,
                format="list",
                confidence=0.0,
                raw_output=output,
                metadata={"error": str(e), "parser": "list"}
            )

    def _extract_list(self, output: str) -> List[str]:
        """提取列表"""
        # 尝试 JSON 格式
        try:
            json_str = self._extract_json(output)
            if json_str:
                data = json.loads(json_str)
                if isinstance(data, list):
                    return [str(item) for item in data]
        except:
            pass

        # 从文本中提取列表项
        items = []

        # 匹配编号列表
        numbered_items = re.findall(r'^\s*\d+[.)\s]+(.+)$', output, re.MULTILINE)
        if numbered_items:
            return numbered_items

        # 匹配符号列表
        bullet_items = re.findall(r'^\s*[-*•]\s+(.+)$', output, re.MULTILINE)
        if bullet_items:
            return bullet_items

        # 匹配逗号分隔
        if ',' in output:
            return [item.strip() for item in output.split(',')]

        # 匹配换行分隔
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        if len(lines) > 1:
            return lines

        return [output.strip()]

    def _extract_json(self, output: str) -> Optional[str]:
        """提取 JSON"""
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', output, re.DOTALL)
        if json_match:
            return json_match.group(1)
        return None

    def get_format_instructions(self) -> str:
        """获取格式说明"""
        return "请以列表格式返回结果"


class OutputParserManager:
    """输出解析器管理器"""

    def __init__(self):
        self.parsers = {
            'json': JSONOutputParser(),
            'tool_call': ToolCallParser(),
            'csv': CSVOutputParser(),
            'list': ListOutputParser(),
        }

    def parse(
        self,
        output: str,
        parser_type: str = 'json',
        **kwargs
    ) -> ParsedOutput:
        """解析输出"""
        if parser_type not in self.parsers:
            raise ValueError(f"不支持的解析器类型: {parser_type}")

        parser = self.parsers[parser_type]

        # 如果是结构化解析器，需要传入 schema
        if parser_type == 'structured':
            schema = kwargs.get('schema', {})
            parser = StructuredOutputParser(schema)

        return parser.parse(output)

    def register_parser(self, name: str, parser: BaseOutputParser):
        """注册解析器"""
        self.parsers[name] = parser

    def get_format_instructions(self, parser_type: str, **kwargs) -> str:
        """获取格式说明"""
        if parser_type == 'structured':
            schema = kwargs.get('schema', {})
            return StructuredOutputParser(schema).get_format_instructions()

        if parser_type in self.parsers:
            return self.parsers[parser_type].get_format_instructions()

        return "未知格式"

    def list_parsers(self) -> List[str]:
        """列出所有解析器"""
        return list(self.parsers.keys())


# 全局解析器管理器实例
parser_manager = OutputParserManager()


def get_output_parser(parser_type: str, **kwargs) -> BaseOutputParser:
    """获取解析器"""
    if parser_type == 'structured':
        schema = kwargs.get('schema', {})
        return StructuredOutputParser(schema)
    return parser_manager.parsers[parser_type]


def parse_output(output: str, parser_type: str = 'json', **kwargs) -> ParsedOutput:
    """便捷函数：解析输出"""
    return parser_manager.parse(output, parser_type, **kwargs)


def get_format_instructions(parser_type: str, **kwargs) -> str:
    """便捷函数：获取格式说明"""
    return parser_manager.get_format_instructions(parser_type, **kwargs)


# 使用示例
if __name__ == "__main__":
    # 1. JSON 解析
    json_output = '''
    {
      "name": "write_file_tool",
      "arguments": {
        "path": "test.txt",
        "content": "hello"
      }
    }
    '''
    result = parse_output(json_output, 'json')
    print(f"JSON 解析: {result.data}")

    # 2. 工具调用解析
    tool_output = '''
    调用工具 write_file_tool
    参数:
      path: test.txt
      content: hello
    '''
    result = parse_output(tool_output, 'tool_call')
    print(f"工具调用解析: {result.data}")

    # 3. 列表解析
    list_output = '''
    1. 项目A
    2. 项目B
    3. 项目C
    '''
    result = parse_output(list_output, 'list')
    print(f"列表解析: {result.data}")

    # 4. 结构化解析
    schema = {
        "name": str,
        "age": int,
        "email": str,
        "active": bool
    }
    structured_output = '''
    name: 张三
    age: 25
    email: zhangsan@example.com
    active: true
    '''
    result = parse_output(structured_output, 'structured', schema=schema)
    print(f"结构化解析: {result.data}")
