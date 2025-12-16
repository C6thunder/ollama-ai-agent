"""通用常量定义

包含项目中使用的各种常量，如文件类型、状态码等
"""

# 文件扩展名常量
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.java', '.cpp', '.c', '.h',
    '.json', '.yaml', '.yml', '.xml', '.csv', '.log',
    '.html', '.css', '.sh', '.sql', '.rst'
}

# 默认配置
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_MAX_MESSAGES = 100
DEFAULT_MAX_INPUT_LENGTH = 10000
DEFAULT_MAX_FILE_SIZE = 100000
DEFAULT_MAX_READ_SIZE = 10000
DEFAULT_COMMAND_TIMEOUT = 10

# 安全配置
MAX_PATH_LENGTH = 4096
MAX_RECURSION_DEPTH = 100

# 日志配置
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = "INFO"

# RAG 配置
DEFAULT_TOP_K = 5
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
SIMILARITY_THRESHOLD = 0.5

# 向量维度
DEFAULT_VECTOR_DIMENSION = 384
