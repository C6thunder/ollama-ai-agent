# AI Agent 项目 - LangChain 功能完整实现

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-1.2%2B-green.svg)](https://python.langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于 LangChain 的完整 AI Agent 项目，实现了 LangChain 的所有核心功能模块，包括 Prompt 管理、数据加载、向量存储、RAG、输出解析、工作流链等。

## ✨ 项目特色

- 🎯 **完整功能实现** - 实现了 LangChain 的所有核心模块
- 🔒 **安全加固** - 内置多层安全验证机制
- 🏗️ **模块化设计** - 清晰的项目结构，易于扩展
- ⚙️ **配置驱动** - 灵活的配置系统
- 🛠️ **自动工具管理** - 智能工具发现和注册
- 🤖 **实时 RAG 支持** - 内置向量存储和检索功能
- 🧪 **LLM 集成** - 支持真实的问答生成

## 🚀 安装

### 前置要求

- Python 3.8 或更高版本
- Conda 或 Miniconda
- Ollama (可选，用于本地 LLM)

### 1. 创建 Conda 环境

```bash
# 创建新的 conda 环境
conda create -n ai-agent python=3.10

# 激活环境
conda activate ai-agent
```

### 2. 安装 Ollama

如果您想使用本地 LLM：

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull qwen2.5-coder:7b
```

### 3. 安装项目依赖

```bash
# 克隆项目
git clone <repository-url>
cd ai-agent-project

# 安装依赖
pip install -r requirements.txt
```


## 🎯 快速开始

### 方式 1：运行 Agent (推荐)

```bash
python agent_secure.py
```

然后在提示符下输入命令：

```
>> !help                    # 查看帮助
>> !load test_all.py        # 加载文档
>> !ask 文档中说了什么？      # RAG 问答
>> !math 10+5*2             # 数学计算
>> !date                    # 查看日期
>> exit                     # 退出
```

### 方式 2：运行示例

```bash
python examples/complete_example.py
```

### 方式 3：在代码中使用

```python
import sys
sys.path.insert(0, 'src')

from core.prompts import get_prompt_manager
from core.vector_store import InMemoryVectorStore, RAGSystem
from core.chains import SimpleChain

# 使用 Prompt 管理器
prompt_manager = get_prompt_manager()
prompt = prompt_manager.get_prompt("system_intro")

# 创建 RAG 系统
vector_store = InMemoryVectorStore()
rag = RAGSystem(vector_store)

# 添加文档并查询
rag.add_documents(documents)
result = rag.query("问题")
print(result['answer'])

# 使用链
chain = SimpleChain(lambda x: x.upper())
result = chain.run(text="hello")
```


## 🌟 功能特性

### 1. Prompt 模块 (`src/core/prompts.py`)

- 预定义 Prompt 模板（系统提示、文件操作、代码生成等）
- 动态 Prompt 生成
- Prompt 构建器
- Prompt 增强器
- 缓存机制

```python
from core.prompts import get_prompt_manager

prompt_manager = get_prompt_manager()
system_prompt = prompt_manager.get_prompt(
    "system_intro",
    tool_descriptions="列出所有可用工具..."
)
```

### 2. 数据加载器 (`src/core/data_loaders.py`)

- 支持多种格式：TXT、MD、PY、JSON、YAML、CSV、HTML 等
- 目录批量加载
- 自动分块
- 元数据提取

```python
from core.data_loaders import load_documents

# 加载单个文件
documents = load_documents('example.txt')

# 加载整个目录
documents = load_documents('./docs', 'directory')

# 加载 JSON 文件
documents = load_documents('data.json', 'json')
```

### 3. 向量存储与 RAG (`src/core/vector_store.py`)

- InMemoryVectorStore 内存向量存储
- TF-IDF 嵌入和简单字符嵌入
- 语义搜索
- 混合搜索（向量 + 关键词）
- 检索增强生成（支持 LLM）

```python
from core.vector_store import InMemoryVectorStore, RAGSystem

vector_store = InMemoryVectorStore()
rag = RAGSystem(vector_store, llm=llm)

# 添加文档
rag.add_documents(documents)

# 问答
result = rag.query("文档中说了什么？")
```

### 4. 输出解析器 (`src/core/output_parsers.py`)

- JSON 解析
- 工具调用解析
- CSV 解析
- 结构化数据解析
- 列表解析

```python
from core.output_parsers import parse_output

# JSON 解析
result = parse_output(json_str, 'json')

# 工具调用解析
result = parse_output(tool_call_str, 'tool_call')

# 列表解析
result = parse_output(list_str, 'list')
```

### 5. 实用工具 (`src/common/utilities/`)

- **MathUtils** - 数学计算（统计、几何、代数）
- **DateUtils** - 日期时间处理
- **FileUtils** - 文件操作
- **SystemUtils** - 系统信息
- **ValidationUtils** - 数据验证
- **TextUtils** - 文本处理

```python
from common.utilities import MathUtils, DateUtils, ValidationUtils, TextUtils

# 数学计算
result = MathUtils.mean([1, 2, 3, 4, 5])

# 日期处理
today = DateUtils.today()
weekday = DateUtils.get_day_of_week(today)

# 数据验证
is_valid = ValidationUtils.is_email("user@example.com")

# 文本处理
clean_text = TextUtils.remove_whitespace("  Hello  ")
```

### 6. 工作流链 (`src/core/chains.py`)

- 顺序链
- 并行链
- 条件链
- LLM 链
- 检索问答链
- 转换链
- 文档组合链

```python
from core.chains import SimpleChain, SequentialChain, ParallelChain

# 创建简单链
transform = SimpleChain(lambda x: x.upper())

# 顺序链
pipeline = chain1 | chain2 | chain3

# 并行链
parallel = chain1 & chain2
```

### 7. Agent 系统 (`agent_secure.py`)

- 安全的 AI Agent 实现
- 自动工具管理
- RAG 集成
- LLM 集成
- 特殊命令支持

## 💬 使用示例

### 示例 1：基本 RAG 问答

```python
import sys
sys.path.insert(0, 'src')

from core.vector_store import InMemoryVectorStore, RAGSystem
from core.data_loaders import Document
from langchain_ollama import ChatOllama

# 创建 LLM
llm = ChatOllama(model="qwen2.5-coder:7b")

# 创建 RAG 系统
vector_store = InMemoryVectorStore()
rag = RAGSystem(vector_store, llm=llm)

# 添加文档
documents = [
    Document(
        content="Python是一种高级编程语言，简洁易读。",
        metadata={"source": "doc1"},
        source="doc1.txt"
    )
]
rag.add_documents(documents)

# 问答
result = rag.query("Python 有什么特点？")
print(result['answer'])  # LLM 生成的答案
```

### 示例 2：使用链处理数据

```python
from core.chains import SimpleChain

# 创建处理链
def clean_text(**kwargs):
    text = kwargs.get('text', '')
    return {'cleaned': text.strip().lower()}

def count_words(**kwargs):
    text = kwargs.get('cleaned', '')
    return {'word_count': len(text.split())}

# 构建链
clean_chain = SimpleChain(clean_text)
count_chain = SimpleChain(count_words)

# 使用链
result = await (clean_chain | count_chain).run(text="  Hello World  ")
print(result)  # {'word_count': 2}
```

### 示例 3：使用实用工具

```python
from common.utilities import MathUtils, DateUtils, ValidationUtils

# 数学计算
numbers = [1, 2, 3, 4, 5]
print(f"平均值: {MathUtils.mean(numbers)}")
print(f"中位数: {MathUtils.median(numbers)}")
print(f"标准差: {MathUtils.std(numbers)}")

# 日期处理
today = DateUtils.today()
print(f"今天: {DateUtils.format_date(today)}")
print(f"星期: {DateUtils.get_day_of_week(today)}")

# 数据验证
emails = ["user@example.com", "invalid-email"]
for email in emails:
    print(f"{email}: {ValidationUtils.is_email(email)}")
```

## 🔧 Agent 特殊命令

Agent 支持以下特殊命令（以开头）：

| `!`  命令 | 说明 | 示例 |
|------|------|------|
| `!help` | 显示帮助 | `!help` |
| `!tools` | 列出所有工具 | `!tools` |
| `!math` | 数学计算 | `!math 10+5*2` |
| `!date` | 显示日期时间 | `!date` |
| `!system` | 显示系统信息 | `!system` |
| `!validate` | 验证数据 | `!validate user@example.com` |
| `!text` | 文本处理 | `!text Hello World` |
| `!load` | 加载文档到 RAG | `!load ./docs` |
| `!ask` | 向 RAG 提问 | `!ask 文档中说了什么？` |
| `!chain` | 演示链功能 | `!chain` |

### 使用示例

```bash
>> !math (10+5)*2
结果: 30

>> !validate user@example.com
✅ 有效的邮箱地址

>> !load ./docs
✅ 已加载 10 个文档到RAG系统

>> !ask 文档中说了什么？
问题: 文档中说了什么？
答案: 根据加载的文档内容...
置信度: 0.85
```

## ⚙️ 配置说明

主要配置在 `config/config.json` 中：

```json
{
  "model": {
    "name": "qwen2.5-coder:7b",
    "temperature": 0.2,
    "num_ctx": 8192
  },
  "security": {
    "max_input_length": 10000,
    "blocked_commands": ["rm", "del", "format"],
    "blocked_directories": ["C:\\", "/etc", "/root"],
    "dangerous_patterns": ["eval\\(", "exec\\("]
  },
  "tools": {
    "command_timeout": 30,
    "max_file_size": 10485760
  }
}
```

## 🛡️ 安全特性

1. **输入验证**
   - 输入长度限制
   - 危险字符过滤
   - SQL 注入防护
   - XSS 防护

2. **路径安全**
   - 路径遍历防护
   - 目录白名单/黑名单
   - 符号链接检查

3. **命令安全**
   - 命令黑名单
   - 危险模式检测
   - 命令超时控制

4. **文件安全**
   - 文件大小限制
   - 文件扩展名过滤
   - 写入路径验证


## 📚 API 参考

### Prompt 管理器

```python
from core.prompts import get_prompt_manager

manager = get_prompt_manager()

# 获取预定义模板
prompt = manager.get_prompt("system_intro", tool_descriptions="...")

# 注册自定义模板
manager.register_template("custom", template)

# 列出所有模板
templates = manager.list_templates()
```

### RAG 系统

```python
from core.vector_store import InMemoryVectorStore, RAGSystem

# 创建 RAG 系统
vector_store = InMemoryVectorStore()
rag = RAGSystem(vector_store, llm=llm)

# 添加文档
rag.add_documents(documents)

# 问答
result = rag.query(
    question="问题内容",
    k=5,              # 返回文档数
    filter=None,      # 元数据过滤
    rerank=True       # 是否重排序
)

# 批量问答
results = rag.batch_query(questions)

# 只检索文档
docs = rag.get_relevant_docs(question, k=5)
```


## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd ai-agent-project

# 创建开发环境
conda create -n ai-agent-dev python=3.10
conda activate ai-agent-dev

# 安装依赖
pip install -r requirements.txt

# 安装开发工具
pip install pytest black flake8 mypy
```



## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下项目：
- [LangChain](https://python.langchain.com) - LLM 应用开发框架
- [Ollama](https://ollama.com) - 本地 LLM 运行工具
- [LangChain-Ollama](https://python.langchain.com/docs/integrations/chat/ollama) - LangChain Ollama 集成



## ⭐ 支持

如果这个项目对您有帮助，请给它一个星标！⭐

---

**Happy Coding! 🎉**
