#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具模块初始化
导出所有可用工具
"""

from .shell_tools import (
    ShellTool,
    PwdTool,
    WhoamiTool,
    DateTool,
    LsTool,
    EnvTool
)

from .file_tools import (
    FileReadTool,
    FileWriteTool,
    FileListTool,
    FileDeleteTool,
    FileCopyTool
)

from .system_tools import (
    SystemInfoTool,
    DiskUsageTool,
    ProcessListTool
)

from .network_tools import (
    HttpGetTool,
    HttpPostTool,
    WebSearchTool,
    DownloadTool
)

from .data_tools import (
    JsonParseTool,
    JsonStringifyTool,
    DataAnalyzeTool,
    DataFilterTool,
    DataSortTool
)


def get_all_tools() -> dict:
    """
    获取所有可用工具的字典

    Returns:
        {工具名: 工具实例}
    """
    tools = [
        # Shell 工具
        ShellTool(),
        PwdTool(),
        WhoamiTool(),
        DateTool(),
        LsTool(),
        EnvTool(),

        # 文件工具
        FileReadTool(),
        FileWriteTool(),
        FileListTool(),
        FileDeleteTool(),
        FileCopyTool(),

        # 系统工具
        SystemInfoTool(),
        DiskUsageTool(),
        ProcessListTool(),

        # 网络工具
        HttpGetTool(),
        HttpPostTool(),
        WebSearchTool(),
        DownloadTool(),

        # 数据工具
        JsonParseTool(),
        JsonStringifyTool(),
        DataAnalyzeTool(),
        DataFilterTool(),
        DataSortTool()
    ]

    return {tool.name: tool for tool in tools}


def get_tool_descriptions() -> dict:
    """获取所有工具的描述"""
    tools = get_all_tools()
    return {name: tool.description for name, tool in tools.items()}


__all__ = [
    # Shell
    'ShellTool', 'PwdTool', 'WhoamiTool', 'DateTool', 'LsTool', 'EnvTool',
    # File
    'FileReadTool', 'FileWriteTool', 'FileListTool', 'FileDeleteTool', 'FileCopyTool',
    # System
    'SystemInfoTool', 'DiskUsageTool', 'ProcessListTool',
    # Network
    'HttpGetTool', 'HttpPostTool', 'WebSearchTool', 'DownloadTool',
    # Data
    'JsonParseTool', 'JsonStringifyTool', 'DataAnalyzeTool', 'DataFilterTool', 'DataSortTool',
    # Functions
    'get_all_tools', 'get_tool_descriptions'
]
