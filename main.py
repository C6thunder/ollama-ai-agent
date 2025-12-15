#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain Agent with Memory - 主入口文件
基于 LangChain 框架的智能代理，集成了强大的记忆系统

用法:
    python main.py              # 交互式模式
    python main.py -t "任务"     # 单次任务模式
    python main.py --list-tools  # 列出所有工具
    python main.py --memory-stats # 查看记忆统计
    python main.py --memory-search "关键词" # 搜索记忆
"""

import sys
import os
import argparse
from typing import List, Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import (
    MemoryManager,
    MemoryAwareAgentBuilder,
    get_agent_config,
    get_config_value
)
from tools import get_all_tools, get_tool_descriptions
from tools.memory_tools import get_memory_tools
from api.llm import OllamaAPI


class MemoryAgentRunner:
    """带记忆的 Agent 运行器"""

    def __init__(self, session_id: Optional[str] = None):
        """
        初始化记忆 Agent

        Args:
            session_id: 会话ID，为空则自动生成
        """
        self.config = self._load_config()
        self.llm = self._init_llm()
        self.tools = get_all_tools()
        self.memory_manager = MemoryManager(session_id=session_id)
        self.memory_tools = get_memory_tools(self.memory_manager)
        self.current_time = self._update_current_time()
        self.agent = self._init_agent()

    def _update_current_time(self):
        """自动更新时间"""
        if "date" in self.tools:
            try:
                result = self.tools["date"].execute()
                if result.get("success"):
                    import json
                    time_info = {
                        "datetime": result.get('datetime', 'N/A'),
                        "timestamp": result.get('timestamp', 'N/A')
                    }
                    print("\n" + "="*50)
                    print("  系统时间已更新")
                    print("="*50)
                    print(f"当前时间: {time_info['datetime']}")
                    print(f"时间戳: {time_info['timestamp']}")
                    print()
                    return time_info
            except Exception as e:
                print(f"警告: 更新时间失败 - {e}")
        return None

    def _load_config(self) -> dict:
        """从配置文件加载配置"""
        config = get_agent_config()

        # 确保所有必需的配置都存在
        if "agent" not in config:
            config["agent"] = {}
        if "model" not in config:
            config["model"] = {}

        # 设置默认值
        config["agent"].setdefault("max_iterations", 10)
        config["agent"].setdefault("verbose", True)
        config["model"].setdefault("name", "qwen2.5:7b")
        config["model"].setdefault("host", "127.0.0.1")
        config["model"].setdefault("port", 11434)

        return config

    def _init_llm(self):
        """初始化 LLM"""
        model_config = self.config.get("model", {})

        # 解析 base_url 获取 host 和 port
        base_url = model_config.get("base_url", "http://127.0.0.1:11434")
        if "://" in base_url:
            host_port = base_url.split("://")[1]
            if ":" in host_port:
                host, port_str = host_port.rsplit(":", 1)
                port = int(port_str)
            else:
                host = host_port
                port = 11434
        else:
            host = "127.0.0.1"
            port = 11434

        llm = OllamaAPI(
            model=model_config.get("name", "qwen2.5:7b"),
            host=host,
            port=port
        )
        return llm

    def _init_agent(self):
        """初始化带记忆的 Agent"""
        agent = MemoryAwareAgentBuilder.create_agent(
            llm_client=self.llm,
            base_tools=self.tools,
            memory_tools=self.memory_tools,
            max_iterations=self.config.get("agent", {}).get("max_iterations", 10),
            verbose=self.config.get("agent", {}).get("verbose", True),
            current_time=self.current_time
        )
        return agent

    def check_services(self) -> dict:
        """检查服务状态"""
        stats = self.memory_manager.get_stats()
        return {
            "ollama": self.llm.is_available(),
            "tools": len(self.tools),
            "memory_tools": len(self.memory_tools),
            "session_id": stats['session_id'],
            "conversation_entries": stats['total_entries'],
            "long_term_entries": stats['long_term_count']
        }

    def list_tools(self):
        """列出所有工具"""
        print("\n=== 可用工具列表 ===\n")

        # 普通工具
        print("## 普通工具\n")
        descriptions = get_tool_descriptions()
        for name, desc in sorted(descriptions.items()):
            print(f"  {name:20} - {desc}")

        # 记忆工具
        print("\n## 记忆工具\n")
        memory_descriptions = {
            "memory_search": "搜索记忆库中的相关信息",
            "memory_list": "列出所有记忆条目",
            "memory_context": "获取当前对话的上下文记忆",
            "memory_clear": "清空对话记忆",
            "memory_stats": "获取记忆使用统计"
        }
        for name, desc in sorted(memory_descriptions.items()):
            print(f"  {name:20} - {desc}")

        print(f"\n共 {len(descriptions) + len(memory_descriptions)} 个工具\n")

    def run_task(self, task: str) -> str:
        """执行单个任务"""
        return self.agent.run(task)

    def search_memory(self, query: str):
        """搜索记忆"""
        results = self.agent.search_memory(query)

        if not results:
            print(f"\n未找到包含 '{query}' 的记忆")
            return

        print(f"\n找到 {len(results)} 条相关记忆:\n")
        for i, result in enumerate(results, 1):
            print(f"[{i}] [{result['type']}] (重要性: {result['importance']:.2f})")
            print(f"    {result['content'][:150]}...")
            print()

    def show_memory_stats(self):
        """显示记忆统计"""
        stats = self.memory_manager.get_stats()

        print("\n" + "="*50)
        print("  记忆统计")
        print("="*50)
        print(f"\n会话ID: {stats['session_id']}")
        print(f"对话条目: {stats['total_entries']}")
        print(f"长期记忆: {stats['long_term_count']}")
        print(f"会话时长: {stats['session_duration']:.1f} 秒")
        print(f"平均重要性: {stats['avg_importance']:.2f}")

        if stats['type_counts']:
            print("\n类型分布:")
            for mem_type, count in stats['type_counts'].items():
                print(f"  - {mem_type}: {count}")

        print("\n" + "="*50)

    def show_memory_summary(self):
        """显示记忆摘要"""
        print(self.agent.get_memory_summary())

    def clear_memory(self):
        """清空记忆"""
        self.agent.clear_memory()
        print("\n记忆已清空")

    def export_memory(self, filepath: str):
        """导出记忆"""
        self.agent.export_memory(filepath)
        print(f"\n记忆已导出到: {filepath}")

    def run_interactive(self):
        """交互式运行"""
        print("=" * 50)
        print("  LangChain Agent with Memory")
        print("=" * 50)

        # 检查服务
        status = self.check_services()
        print(f"\nOllama: {'✓ 可用' if status['ollama'] else '✗ 不可用'}")
        print(f"工具数: {status['tools']} (+{status['memory_tools']} 记忆工具)")
        print(f"会话ID: {status['session_id']}")
        print(f"记忆条目: {status['conversation_entries']} (长期: {status['long_term_entries']})")

        if not status['ollama']:
            print("\n错误: Ollama 服务不可用，请先启动 Ollama")
            return

        print("\n命令:")
        print("  exit/quit  - 退出")
        print("  tools      - 列出工具")
        print("  history    - 查看对话历史")
        print("  memory     - 显示记忆摘要")
        print("  mem-stats  - 显示记忆统计")
        print("  mem-search - 搜索记忆 (mem-search <关键词>)")
        print("  mem-clear  - 清空记忆")
        print("  mem-export - 导出记忆 (mem-export <文件路径>)")
        print()

        while True:
            try:
                task = input("\n>> ").strip()

                if not task:
                    continue

                # 解析命令
                if task.lower() in ["exit", "quit", "q"]:
                    print("\n再见!")
                    # 保存会话
                    self.memory_manager.save_session()
                    break

                elif task.lower() == "tools":
                    self.list_tools()

                elif task.lower() == "history":
                    history = self.agent.get_history()
                    if history:
                        for i, h in enumerate(history, 1):
                            print(f"\n[{i}] 任务: {h['task'][:50]}...")
                            print(f"    答案: {h['answer'][:100]}...")
                    else:
                        print("暂无历史记录")

                elif task.lower() == "memory":
                    self.show_memory_summary()

                elif task.lower() == "mem-stats":
                    self.show_memory_stats()

                elif task.lower().startswith("mem-search "):
                    query = task[len("mem-search "):].strip()
                    if query:
                        self.search_memory(query)
                    else:
                        print("请提供搜索关键词")

                elif task.lower() == "mem-clear":
                    confirm = input("\n确定要清空记忆吗？(y/N): ").strip().lower()
                    if confirm == 'y':
                        self.clear_memory()

                elif task.lower().startswith("mem-export "):
                    filepath = task[len("mem-export "):].strip()
                    if filepath:
                        self.export_memory(filepath)
                    else:
                        print("请提供文件路径")

                else:
                    result = self.run_task(task)
                    print(f"\n{'=' * 50}")
                    print("最终答案:")
                    print(result)

            except KeyboardInterrupt:
                print("\n\n中断，再见!")
                # 保存会话
                self.memory_manager.save_session()
                break
            except Exception as e:
                print(f"\n错误: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="LangChain Agent with Memory - 基于 LangChain 的智能代理"
    )
    parser.add_argument("-t", "--task", help="执行单个任务")
    parser.add_argument("--list-tools", action="store_true", help="列出所有工具")
    parser.add_argument("--session-id", help="指定会话ID")
    parser.add_argument("--memory-stats", action="store_true", help="显示记忆统计")
    parser.add_argument("--memory-search", help="搜索记忆")
    parser.add_argument("--memory-export", help="导出记忆到文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    runner = MemoryAgentRunner(session_id=args.session_id)

    if args.list_tools:
        runner.list_tools()
    elif args.task:
        result = runner.run_task(args.task)
        print(f"\n结果: {result}")
    elif args.memory_stats:
        runner.show_memory_stats()
    elif args.memory_search:
        runner.search_memory(args.memory_search)
    elif args.memory_export:
        runner.export_memory(args.memory_export)
    else:
        runner.run_interactive()


if __name__ == "__main__":
    main()
