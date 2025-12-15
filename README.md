# LangChain Agent with Memory

基于 LangChain 框架的智能代理，集成了强大的记忆系统，支持与 Ollama 模型无缝集成。

## ✨ 项目特性

### 🚀 核心功能
- **LangChain 框架** - 基于业界领先的 LLM 应用开发框架
- **ReAct Agent** - 支持推理和行动交替执行的智能代理
- **双层记忆系统** - 短期记忆（对话历史）+ 长期记忆（持久化存储）
- **Ollama 模型支持** - 本地部署的 LLM 模型，无需云端服务
- **丰富的工具集** - 文件操作、Shell 命令、网络搜索、记忆管理等
- **配置驱动** - 灵活的 JSON 配置文件，无需硬编码

### 🛠️ 可用工具

#### 普通工具
- **file_read** - 读取文件内容
- **file_write** - 写入文件内容
- **file_list** - 列出目录内容
- **file_delete** - 删除文件（安全保护）
- **file_copy** - 复制文件
- **shell** - 执行 Shell 命令（安全白名单）
- **pwd** - 获取当前工作目录
- **whoami** - 获取当前用户名
- **date** - 获取当前日期时间
- **ls** - 列出目录内容
- **env** - 获取环境变量
- **http_get** - HTTP GET 请求
- **http_post** - HTTP POST 请求
- **web_search** - 网络搜索（支持 DuckDuckGo、百度等）
- **download** - 文件下载

#### 记忆工具
- **memory_search** - 搜索记忆库中的相关信息
- **memory_list** - 列出所有记忆条目
- **memory_context** - 获取当前对话的上下文记忆
- **memory_clear** - 清空对话记忆
- **memory_stats** - 获取记忆使用统计

## 📋 系统要求

- Python 3.8+
- Ollama 本地服务
- 必要的 Python 依赖包

## 🔧 安装与配置

### 1. 安装 Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
从 [Ollama 官网](https://ollama.ai) 下载安装包

### 2. 启动 Ollama 服务

```bash
ollama serve
```

### 3. 安装模型

```bash
# 安装 qwen2.5:7b 模型（推荐）
ollama pull qwen2.5:7b

# 或安装其他模型
ollama pull llama3.1:8b
ollama pull mistral:7b
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置模型

编辑 `config/agent_config.json`:

```json
{
  "model": {
    "provider": "ollama",
    "name": "qwen2.5:7b",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

## 🚀 使用方法

### 交互式模式

启动交互式会话：

```bash
python main.py
```

**交互命令：**
- `exit/quit/q` - 退出程序
- `tools` - 列出所有可用工具
- `history` - 查看对话历史
- `memory` - 显示记忆摘要
- `mem-stats` - 显示记忆统计
- `mem-search <关键词>` - 搜索记忆
- `mem-clear` - 清空记忆
- `mem-export <文件路径>` - 导出记忆

### 单次任务模式

执行单个任务：

```bash
python main.py -t "请读取 /home/user/documents/readme.txt 文件内容"
```

### 其他命令

```bash
# 列出所有工具
python main.py --list-tools

# 查看记忆统计
python main.py --memory-stats

# 搜索记忆
python main.py --memory-search "关键词"

# 导出记忆
python main.py --memory-export memory.json

# 指定会话 ID
python main.py --session-id my-session-001
```

## 📁 项目结构

```
/home/thunder/AI/
├── main.py                    # 主入口文件
├── config/                    # 配置文件目录
│   ├── agent_config.json     # Agent 和模型配置
│   └── tools_config.json     # 工具配置
├── core/                      # 核心模块
│   ├── config_loader.py      # 配置加载器
│   ├── memory.py             # 记忆管理系统
│   ├── memory_agent.py       # 记忆感知代理
│   └── __init__.py
├── tools/                     # 工具模块
│   ├── file_tools.py         # 文件操作工具
│   ├── shell_tools.py        # Shell 工具
│   ├── network_tools.py      # 网络工具
│   ├── memory_tools.py       # 记忆工具
│   └── __init__.py
├── api/                       # API 模块
│   └── llm.py               # LLM 接口
├── memory/                    # 记忆存储目录
│   └── sessions/            # 会话记忆
└── logs/                     # 日志目录
```

## ⚙️ 配置说明

### Agent 配置 (config/agent_config.json)

```json
{
  "agent": {
    "name": "ReAct-Agent",
    "version": "2.0.0",
    "max_iterations": 10,        # 最大迭代次数
    "timeout": 60,               # 超时时间（秒）
    "verbose": true,             # 详细输出
    "auto_check": true           # 自动检查服务
  },
  "model": {
    "provider": "ollama",        # 模型提供商
    "name": "qwen2.5:7b",        # 模型名称
    "base_url": "http://localhost:11434",  # Ollama 服务地址
    "temperature": 0.7,          # 温度参数
    "max_tokens": 4096           # 最大 token 数
  },
  "logging": {
    "level": "INFO",             # 日志级别
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/agent.log"     # 日志文件
  }
}
```

### 工具配置 (config/tools_config.json)

```json
{
  "tools": {
    "shell": {
      "enabled": true,
      "timeout": 30,                     # 命令超时时间
      "safe_commands": [...],            # 安全命令白名单
      "dangerous_commands": [...]        # 危险命令黑名单
    },
    "file": {
      "enabled": true,
      "max_file_size": 10485760,         # 最大文件大小（10MB）
      "allowed_extensions": [...],       # 允许的文件扩展名
      "protected_paths": [               # 保护路径
        "/etc", "/usr", "/bin", "/sbin", "/boot", "/root"
      ]
    },
    "network": {
      "enabled": true,
      "timeout": 30,                     # 网络请求超时
      "max_download_size": 104857600,    # 最大下载大小（100MB）
      "allowed_protocols": ["http", "https"]
    }
  }
}
```

## 🎯 使用示例

### 示例 1: 文件操作

```python
# 读取文件
python main.py -t "读取 /home/user/data.txt 文件内容"

# 写入文件
python main.py -t "在 /home/user/test.txt 中写入 'Hello World'"

# 列出目录
python main.py -t "列出 /home/user/documents 目录内容"
```

### 示例 2: 网络搜索

```python
python main.py -t "搜索 'Python LangChain' 并返回前5个结果"
```

### 示例 3: Shell 命令

```python
python main.py -t "执行 'ls -la /home' 命令"
```

### 示例 4: 记忆管理

```
>> memory                    # 显示记忆摘要
>> mem-search "配置"         # 搜索包含"配置"的记忆
>> mem-stats                 # 查看记忆统计
```

## 🔒 安全特性

### 文件操作安全
- **路径保护** - 防止访问系统关键目录
- **文件大小限制** - 避免处理过大文件
- **用户目录访问** - 允许在用户主目录进行操作

### Shell 命令安全
- **命令白名单** - 仅允许执行预定义的安全命令
- **危险模式检测** - 阻止潜在的恶意命令
- **超时控制** - 防止命令长时间运行

### 网络安全
- **协议限制** - 仅允许 HTTP/HTTPS 协议
- **超时控制** - 防止网络请求挂起
- **大小限制** - 限制下载文件大小

## 🧠 记忆系统

### 短期记忆
- 存储当前对话的所有交互
- 包含任务、思考过程、行动和答案
- 自动持久化到会话文件

### 长期记忆
- 持久化存储重要信息
- 基于重要性评分自动筛选
- 支持全文搜索和语义搜索

### 记忆统计
- 总条目数
- 类型分布（任务、思考、行动、答案）
- 平均重要性评分
- 会话时长

## 📊 性能优化

### 配置调优
- 调整 `max_iterations` 控制代理迭代次数
- 修改 `temperature` 控制模型创造性
- 设置合适的 `timeout` 避免长时间等待

### 模型选择
- **qwen2.5:7b** - 平衡性能和资源消耗（推荐）
- **llama3.1:8b** - 更高的推理能力
- **mistral:7b** - 轻量级选项

## 🐛 常见问题

### Q: Ollama 服务不可用
**A:** 确保 Ollama 服务正在运行：
```bash
ollama serve
```

### Q: 模型下载失败
**A:** 检查网络连接，或尝试使用代理：
```bash
ollama pull qwen2.5:7b
```

### Q: 文件操作被拒绝
**A:** 检查文件路径是否在保护目录内，或位于用户主目录

### Q: 记忆搜索无结果
**A:** 确保记忆中有相关内容，或使用 `mem-list` 查看所有记忆

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用开发框架
- [Ollama](https://ollama.ai) - 本地 LLM 部署方案
- [qwen2.5](https://github.com/QwenLM) - 通义千问模型

---

**🎊 享受与 LangChain Agent 的智能对话体验！**
