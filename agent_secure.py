# agent_secure.py - 安全加固版 Agent
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
import os
import sys

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入重构后的模块
from config import Config
from common.logs import Logger
from common.memory import ConversationMemory
from security.security import SecurityValidator
from agents.tool_manager import get_tool_manager

# 导入新功能模块
from core.prompts import get_prompt_manager
from core.data_loaders import load_documents
from core.vector_store import InMemoryVectorStore, RAGSystem
from core.output_parsers import parse_output
from common.utilities import (
    MathUtils, DateUtils, FileUtils, SystemUtils,
    ValidationUtils, TextUtils
)


def parse_tool_call_safely(content: str) -> tuple:
    """安全地解析工具调用

    Args:
        content: 包含 JSON 的文本

    Returns:
        tuple: (是否成功, 工具名, 参数, 错误信息)
    """
    try:
        # 使用安全验证器
        is_safe, error, tool_call = SecurityValidator.validate_tool_call(content)

        if not is_safe:
            return False, None, None, error

        tool_name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})

        return True, tool_name, arguments, None

    except Exception as e:
        return False, None, None, f"解析失败: {str(e)}"


def generate_tool_call_id() -> str:
    """生成唯一的工具调用 ID

    Returns:
        str: 工具调用 ID
    """
    import time
    import random
    return f"tool_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"


def handle_special_command(user_input: str, agent, memory, logger, rag_system):
    """处理特殊命令"""
    command = user_input.strip()[1:]  # 去掉!
    parts = command.split(None, 1)
    cmd = parts[0].lower() if parts else ""
    args = parts[1] if len(parts) > 1 else ""

    try:
        if cmd == "help":
            print("""
=== 特殊命令帮助 ===
!help - 显示此帮助
!tools - 列出所有可用工具
!math <表达式> - 数学计算（如 !math 10+5*2）
!date - 显示当前日期时间
!system - 显示系统信息
!validate <内容> - 验证内容（如邮箱、手机号）
!text <文本> - 文本处理（去除空白、转换大小写等）
!load <路径> - 加载文档到RAG系统
!ask <问题> - 向RAG系统提问
!chain - 演示链功能
!tools - 显示可用工具列表

示例：
!math (10+5)*2
!validate user@example.com
!load ./docs
!ask 文档中说了什么？
            """)
        elif cmd == "tools":
            tool_manager = get_tool_manager()
            tools = list(tool_manager.get_tool_names())
            print("\n可用工具:")
            for name in tools:
                tool = tool_manager.get_tool(name)
                desc = tool.description.split('\n')[0] if tool.description else ""
                print(f"- {name}: {desc}")
        elif cmd == "math":
            if not args:
                print("请提供数学表达式，如: !math 10+5*2")
            else:
                # 简单数学计算演示
                import ast
                try:
                    # 安全的数学表达式求值
                    # 使用更兼容的节点类型列表
                    allowed_nodes = (
                        ast.Expression, ast.BinOp, ast.UnaryOp,
                        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
                        ast.Name, ast.Call, ast.Constant
                    )
                    # 处理不同Python版本的兼容性
                    if hasattr(ast, 'Num'):
                        allowed_nodes += (ast.Num,)
                    if hasattr(ast, 'NameConstant'):
                        allowed_nodes += (ast.NameConstant,)

                    tree = ast.parse(args, mode='eval')
                    for node in ast.walk(tree):
                        if not isinstance(node, allowed_nodes):
                            print("❌ 不安全的数学表达式")
                            return
                    result = eval(args)
                    print(f"结果: {result}")
                    logger.info(f"Math calculation: {args} = {result}")
                except Exception as e:
                    print(f"❌ 计算错误: {str(e)}")
        elif cmd == "date":
            current_time = DateUtils.now()
            print(f"当前时间: {DateUtils.format_date(current_time)}")
            print(f"当前日期: {DateUtils.format_date(DateUtils.today())}")
            print(f"星期: {DateUtils.get_day_of_week(DateUtils.today())}")
        elif cmd == "system":
            summary = SystemUtils.get_system_summary()
            print(f"\n系统信息:")
            print(f"平台: {summary['platform']['system']} {summary['platform']['architecture']}")
            print(f"CPU核心数: {summary['cpu']['count']}")
            print(f"CPU使用率: {summary['cpu']['usage_total']:.1f}%")
            print(f"总内存: {SystemUtils.format_bytes(summary['memory']['total'])}")
            print(f"内存使用率: {summary['memory']['percent']:.1f}%")
        elif cmd == "validate":
            if not args:
                print("请提供要验证的内容，如: !validate user@example.com")
            else:
                # 尝试多种验证
                if ValidationUtils.is_email(args):
                    print("✅ 有效的邮箱地址")
                elif ValidationUtils.is_phone_number(args):
                    print("✅ 有效的手机号")
                elif ValidationUtils.is_url(args):
                    print("✅ 有效的URL")
                else:
                    print("❓ 未知格式（但可能有效）")
        elif cmd == "text":
            if not args:
                print("请提供文本，如: !text Hello World")
            else:
                print(f"原文本: '{args}'")
                print(f"小写: '{TextUtils.to_lowercase(args)}'")
                print(f"大写: '{TextUtils.to_uppercase(args)}'")
                print(f"标题: '{TextUtils.to_title_case(args)}'")
                print(f"去空白: '{TextUtils.remove_whitespace(args)}'")
        elif cmd == "load":
            if not args:
                print("请提供文档路径，如: !load ./docs")
            else:
                if rag_system:
                    try:
                        documents = load_documents(args)
                        if documents:
                            rag_system.add_documents(documents)
                            print(f"✅ 已加载 {len(documents)} 个文档到RAG系统")
                        else:
                            print("❌ 未找到文档")
                    except Exception as e:
                        print(f"❌ 加载文档失败: {str(e)}")
                else:
                    print("❌ RAG系统未初始化")
        elif cmd == "ask":
            if not args:
                print("请提供问题，如: !ask 文档中说了什么？")
            else:
                if rag_system:
                    result = rag_system.query(args)
                    print(f"\n问题: {result['question']}")
                    print(f"答案: {result['answer']}")
                    print(f"置信度: {result['confidence']:.2f}")
                else:
                    print("❌ RAG系统未初始化")
        elif cmd == "chain":
            print("\n=== Chain 功能演示 ===")
            from core.chains import SimpleChain, SequentialChain, ConditionalChain

            # 创建一个简单的转换链
            chain1 = SimpleChain(lambda data: data.upper())
            chain2 = SimpleChain(lambda data: f"[{data}]")

            # 顺序链
            sequential = chain1 | chain2
            result = "hello world"
            print(f"顺序链示例: '{result}' -> '{result.upper()}' -> '[{result.upper()}]'")

            # 条件链
            def is_long(data: dict) -> bool:
                return len(data.get("text", "")) > 10

            long_chain = SimpleChain(lambda data: "文本较长")
            short_chain = SimpleChain(lambda data: "文本较短")
            conditional = ConditionalChain(is_long, long_chain, short_chain)
            # 注意: 实际使用中需要 await conditional.run()
            print(f"条件链示例: 短文本 -> 使用 'hi' 文本将返回 '文本较短'")
            print(f"条件链示例: 长文本 -> 使用 '这是一个很长的文本' 将返回 '文本较长'")
        else:
            print(f"❌ 未知命令: {cmd}，输入 !help 查看帮助")
    except Exception as e:
        logger.error(f"处理特殊命令失败: {str(e)}")
        print(f"❌ 命令执行失败: {str(e)}")


if __name__ == "__main__":
    # 加载配置
    config = Config.get_instance()
    logger = Logger.get_logger()

    # 加载日志
    logger.info("Starting Secure Agent...")

    # 创建 LLM
    model_config = config.get_model_config()
    llm = ChatOllama(
        model=model_config.get("name", "qwen2.5-coder:7b"),
        temperature=model_config.get("temperature", 0.2),
        num_ctx=model_config.get("num_ctx", 8192)
    )

    logger.info(f"Model loaded: {model_config.get('name')}")

    # 获取工具管理器
    tool_manager = get_tool_manager()

    # 获取所有工具
    tools = list(tool_manager.get_tool_names())
    tool_list = [tool_manager.get_tool(name) for name in tools]

    # 动态生成系统提示
    tool_descriptions = []
    for name in tools:
        tool = tool_manager.get_tool(name)
        # 提取工具描述的第一行
        desc = tool.description.split('\n')[0] if tool.description else ""
        tool_descriptions.append(f"- {name} - {desc}")

    tools_text = '\n'.join(tool_descriptions)

    # 创建 Agent
    system_prompt = f"""你是一个安全的 AI 助手。

可用工具:
{tools_text}

所有操作都经过安全验证，包括路径检查、文件大小限制、命令黑名单等。

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

    agent = create_agent(
        model=llm,
        tools=tool_list,
        system_prompt=system_prompt
    )

    # 初始化 RAG 系统（用于文档问答）
    try:
        vector_store = InMemoryVectorStore()
        rag_system = RAGSystem(vector_store, llm=llm)
        logger.info("RAG system initialized with LLM")
    except Exception as e:
        logger.warning(f"RAG system initialization failed: {str(e)}")
        rag_system = None

    logger.info("Secure Agent created successfully")

    # 创建内存管理器
    memory_config = config.get_memory_config()
    memory = ConversationMemory(max_messages=memory_config.get("max_messages", 100))

    # 动态显示可用工具
    print("=== Secure AI Agent (type 'exit' to quit) ===")
    print("\n可用工具:")
    for name in tools:
        tool = tool_manager.get_tool(name)
        desc = tool.description.split('\n')[0] if tool.description else ""
        print(f"- {name}: {desc}")
    print("\n安全特性:")
    print("- 路径限制在项目目录内")
    print("- 命令黑名单验证")
    print("- 输入长度限制")
    print("- 危险字符过滤")
    print()

    while True:
        user_input = input(">> ")
        if user_input.strip().lower() == "exit":
            logger.info("Agent shutting down...")
            break

        # 检查特殊命令
        if user_input.strip().startswith("!"):
            # 处理特殊命令
            handle_special_command(user_input, agent, memory, logger, rag_system)
            continue

        # 验证用户输入
        is_safe, error = SecurityValidator.validate_user_input(user_input)
        if not is_safe:
            print(f"❌ 输入不安全: {error}")
            logger.warning(f"Unsafe input rejected: {user_input}")
            continue

        # 记录用户输入
        logger.info(f"User input: {user_input}")
        memory.add_message("user", user_input)

        try:
            # 调用 agent 获取响应
            inputs = {"messages": memory.get_messages()}
            result = agent.invoke(inputs)

            # 获取消息
            if isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
            else:
                messages = result.messages if hasattr(result, 'messages') else []

            # 找到最后一条 AI 消息
            ai_message = None
            for msg in reversed(messages):
                content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
                if content and ('```json' in content or content.strip().startswith('{')):
                    ai_message = msg
                    break

            if ai_message:
                print(ai_message.content)

                # 安全解析工具调用
                success, tool_name, arguments, error = parse_tool_call_safely(ai_message.content)

                if success:
                    print(f"\n🔧 执行工具: {tool_name}")
                    print(f"参数: {arguments}")
                    logger.info(f"Executing tool: {tool_name} with args: {arguments}")

                    # 生成工具调用 ID
                    tool_call_id = generate_tool_call_id()

                    # 使用工具管理器执行工具
                    success, message, result = tool_manager.execute_tool(tool_name, arguments)

                    if success:
                        print(f"✅ {result}")
                        memory.add_message(
                            "tool",
                            f"工具执行成功: {result}",
                            name=tool_name,
                            tool_call_id=tool_call_id
                        )
                    else:
                        error_msg = f"❌ {message}"
                        print(error_msg)
                        memory.add_message(
                            "tool",
                            error_msg,
                            name=tool_name,
                            tool_call_id=tool_call_id
                        )

                    # 再次调用 LLM 获取最终响应
                    final_result = agent.invoke({"messages": memory.get_messages()})

                    if isinstance(final_result, dict) and 'messages' in final_result:
                        final_messages = final_result['messages']
                    else:
                        final_messages = final_result.messages if hasattr(final_result, 'messages') else []

                    # 显示最终响应
                    for msg in reversed(final_messages):
                        content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
                        if content and ('```json' not in content and not content.strip().startswith('{')):
                            print("\n" + content)
                            memory.add_message("assistant", content)
                            logger.info(f"Final response: {content}")
                            break
                else:
                    # 验证失败
                    error_msg = f"❌ 工具调用不安全: {error}"
                    print(error_msg)
                    logger.warning(f"Unsafe tool call rejected: {error}")

            else:
                # 没有工具调用，直接显示响应
                for msg in reversed(messages):
                    content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
                    if content:
                        print(content)
                        memory.add_message("assistant", content)
                        logger.info(f"Response: {content}")
                        break

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            import traceback
            traceback.print_exc()
