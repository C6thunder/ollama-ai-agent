"""完整示例 - LangChain 功能演示

展示如何使用所有 LangChain 功能模块
包括 Prompt、数据加载器、向量存储、输出解析器、实用工具和链
"""

import asyncio
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.prompts import get_prompt_manager, PromptTemplateBuilder
from core.data_loaders import load_documents, Document
from core.vector_store import InMemoryVectorStore, RAGSystem
from core.output_parsers import parse_output
from common.utilities import (
    MathUtils, DateUtils, FileUtils, SystemUtils,
    ValidationUtils, TextUtils
)
from core.chains import SimpleChain, SequentialChain, ParallelChain


def example_1_prompts():
    """示例 1: Prompt 模板管理"""
    print("=" * 60)
    print("示例 1: Prompt 模板管理")
    print("=" * 60)

    prompt_manager = get_prompt_manager()

    # 使用预定义模板
    system_prompt = prompt_manager.get_prompt(
        "system_intro",
        tool_descriptions="- write_file: 写入文件\n- read_file: 读取文件"
    )
    print("系统提示:")
    print(system_prompt)
    print()

    # 使用构建器创建自定义模板
    builder = PromptTemplateBuilder()
    custom_prompt = builder.add_text("你是一个").add_variable("role").add_text("专家。") \
        .add_section("任务", "请执行以下任务:").add_variable("task") \
        .build()

    formatted_prompt = custom_prompt.format(
        role="代码审查",
        task="审查 Python 代码中的安全问题"
    )
    print("自定义 Prompt:")
    print(formatted_prompt)
    print()


def example_2_data_loaders():
    """示例 2: 数据加载器"""
    print("=" * 60)
    print("示例 2: 数据加载器")
    print("=" * 60)

    # 创建示例文档
    sample_text = """这是示例文档。

内容包括：
1. 基础概念
2. 高级特性
3. 使用示例

详细说明请参考文档内容。
"""

    # 模拟从文件加载（实际使用 load_documents 函数）
    documents = [
        Document(
            content=sample_text,
            metadata={"title": "示例文档", "type": "text"},
            source="example.txt"
        )
    ]

    print(f"加载了 {len(documents)} 个文档")
    for doc in documents:
        print(f"文档: {doc.source}")
        print(f"内容长度: {len(doc.content)} 字符")
        print(f"元数据: {doc.metadata}")
    print()


def example_3_vector_store():
    """示例 3: 向量存储和 RAG"""
    print("=" * 60)
    print("示例 3: 向量存储和 RAG")
    print("=" * 60)

    # 创建向量存储
    vector_store = InMemoryVectorStore()
    rag = RAGSystem(vector_store)

    # 添加文档
    documents = [
        Document(
            content="Python是一种高级编程语言，简洁易读。",
            metadata={"source": "doc1"},
            source="doc1.txt"
        ),
        Document(
            content="JavaScript主要用于Web前端开发，也可以用于后端。",
            metadata={"source": "doc2"},
            source="doc2.txt"
        ),
        Document(
            content="Java是一种强类型、面向对象的编程语言。",
            metadata={"source": "doc3"},
            source="doc3.txt"
        )
    ]

    rag.add_documents(documents)
    print(f"添加了 {len(documents)} 个文档到 RAG 系统\n")

    # 查询
    questions = [
        "什么是 Python？",
        "JavaScript 的用途是什么？",
        "比较 Python 和 Java 的特点"
    ]

    for question in questions:
        result = rag.query(question)
        print(f"问题: {result['question']}")
        print(f"答案: {result['answer'][:100]}...")
        print(f"置信度: {result['confidence']:.2f}")
        print(f"相关文档数: {len(result['relevant_documents'])}")
        print()


def example_4_output_parsers():
    """示例 4: 输出解析器"""
    print("=" * 60)
    print("示例 4: 输出解析器")
    print("=" * 60)

    # JSON 解析
    json_output = '''
    {
      "name": "write_file",
      "arguments": {
        "path": "test.txt",
        "content": "Hello, World!"
      }
    }
    '''
    result = parse_output(json_output, 'json')
    print(f"JSON 解析结果:")
    print(f"  数据: {result.data}")
    print(f"  格式: {result.format}")
    print(f"  置信度: {result.confidence}")
    print()

    # 工具调用解析
    tool_output = '''
    工具名: read_file
    参数:
      path: test.txt
    '''
    result = parse_output(tool_output, 'tool_call')
    print(f"工具调用解析结果:")
    if result.data:
        print(f"  工具名: {result.data.get('name')}")
        print(f"  参数: {result.data.get('arguments')}")
    else:
        print(f"  解析失败: {result.metadata.get('error', '未知错误')}")
    print()

    # 列表解析
    list_output = '''
    1. 项目A
    2. 项目B
    3. 项目C
    '''
    result = parse_output(list_output, 'list')
    print(f"列表解析结果:")
    print(f"  项目数: {len(result.data)}")
    print(f"  项目: {result.data}")
    print()


def example_5_utilities():
    """示例 5: 实用工具"""
    print("=" * 60)
    print("示例 5: 实用工具")
    print("=" * 60)

    # 数学工具
    print("数学计算:")
    print(f"  10 + 5 = {MathUtils.add(10, 5)}")
    print(f"  2^10 = {MathUtils.power(2, 10)}")
    print(f"  √16 = {MathUtils.sqrt(16)}")
    print(f"  10! = {MathUtils.factorial(10)}")

    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"  平均值: {MathUtils.mean(numbers):.2f}")
    print(f"  中位数: {MathUtils.median(numbers)}")
    print()

    # 日期工具
    print("日期时间:")
    now = DateUtils.now()
    today = DateUtils.today()
    print(f"  当前时间: {DateUtils.format_date(now)}")
    print(f"  今天日期: {DateUtils.format_date(today)}")
    print(f"  星期: {DateUtils.get_day_of_week(today)}")
    print(f"  月份: {DateUtils.get_month_name(today)}")
    print(f"  是否为闰年: {DateUtils.is_leap_year(today.year)}")
    print()

    # 验证工具
    print("数据验证:")
    test_data = [
        ("user@example.com", "邮箱"),
        ("https://www.example.com", "URL"),
        ("13812345678", "手机号"),
        ("invalid-email", "邮箱")
    ]

    for data, desc in test_data:
        is_email = ValidationUtils.is_email(data)
        is_url = ValidationUtils.is_url(data)
        is_phone = ValidationUtils.is_phone_number(data)
        print(f"  {data} ({desc}):")
        print(f"    邮箱: {is_email}, URL: {is_url}, 手机: {is_phone}")
    print()

    # 文本工具
    print("文本处理:")
    text = "  Hello, World!  "
    print(f"  原文本: '{text}'")
    print(f"  小写: '{TextUtils.to_lowercase(text)}'")
    print(f"  去空白: '{TextUtils.remove_whitespace(text)}'")
    print(f"  标题: '{TextUtils.to_title_case(text.lower())}'")
    print()


async def example_6_chains_async():
    """示例 6: 工作流链（异步版本）"""
    print("=" * 60)
    print("示例 6: 工作流链")
    print("=" * 60)

    # 创建简单链
    def transform1(**kwargs):
        return {"text": kwargs.get("text", "").upper()}

    def transform2(**kwargs):
        return {"text": f"[{kwargs.get('text', '')}]"}

    def transform3(**kwargs):
        return {"text": kwargs.get("text", "").replace(" ", "_")}

    chain1 = SimpleChain(transform1)
    chain2 = SimpleChain(transform2)
    chain3 = SimpleChain(transform3)

    # 顺序链
    print("顺序链示例:")
    sequential = chain1 | chain2 | chain3
    result = await sequential.run(text="hello world")
    print(f"  输入: 'hello world'")
    print(f"  输出: {result}")
    print()

    # 并行链
    print("并行链示例:")
    parallel = chain1 & chain2
    result = await parallel.run(text="hello")
    print(f"  输入: 'hello'")
    print(f"  输出: {result}")
    print()

    # 简单条件演示
    print("条件链示例（简单演示）:")

    def is_long_text(data: dict) -> bool:
        return len(data.get("text", "")) > 10

    data1 = {"text": "hi"}
    data2 = {"text": "这是一个比较长的文本"}

    print(f"  短文本 'hi': {'文本较短' if not is_long_text(data1) else '文本较长'}")
    print(f"  长文本 '这是一个比较长的文本': {'文本较长' if is_long_text(data2) else '文本较短'}")
    print()


def example_6_chains():
    """示例 6: 工作流链 - 包装异步函数"""
    import asyncio
    asyncio.run(example_6_chains_async())


def example_7_complete_rag_system():
    """示例 7: 完整的 RAG 系统"""
    print("=" * 60)
    print("示例 7: 完整的 RAG 系统")
    print("=" * 60)

    # 创建 RAG 系统
    vector_store = InMemoryVectorStore()
    rag = RAGSystem(vector_store)

    # 添加多个文档
    documents = [
        Document(
            content="人工智能（AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
            metadata={"topic": "AI", "source": "ai_intro"},
            source="ai_intro.txt"
        ),
        Document(
            content="机器学习是人工智能的一个分支。机器学习是人工智能的核心，是使计算机具有智能的根本途径。",
            metadata={"topic": "ML", "source": "ml_intro"},
            source="ml_intro.txt"
        ),
        Document(
            content="深度学习是机器学习的子集。它基于人工神经网络的表征学习方法。",
            metadata={"topic": "DL", "source": "dl_intro"},
            source="dl_intro.txt"
        )
    ]

    rag.add_documents(documents)
    print(f"已加载 {len(documents)} 个文档\n")

    # 问答流程
    questions = [
        "什么是人工智能？",
        "机器学习和深度学习的关系是什么？",
        "AI有哪些应用领域？"
    ]

    for question in questions:
        print(f"问题: {question}")
        result = rag.query(question)

        print(f"答案:")
        print(f"  {result['answer']}")
        print(f"置信度: {result['confidence']:.2f}")

        print(f"相关文档:")
        for doc in result['relevant_documents']:
            print(f"  - {doc['metadata'].get('source', 'unknown')}")
        print()


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "=" * 60)
    print("LangChain 功能完整演示")
    print("=" * 60 + "\n")

    try:
        example_1_prompts()
        example_2_data_loaders()
        example_3_vector_store()
        example_4_output_parsers()
        example_5_utilities()
        example_6_chains()
        example_7_complete_rag_system()

        print("=" * 60)
        print("所有示例演示完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
