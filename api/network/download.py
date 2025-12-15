#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件下载模块
"""

import os
import requests
from typing import Dict, Any, Optional


class Downloader:
    """文件下载器"""

    def __init__(self, timeout: int = 60, max_size: int = 100 * 1024 * 1024):
        self.timeout = timeout
        self.max_size = max_size  # 默认最大 100MB

    def download(self, url: str, filepath: str,
                 chunk_size: int = 8192) -> Dict[str, Any]:
        """
        下载文件

        Args:
            url: 文件 URL
            filepath: 保存路径
            chunk_size: 块大小

        Returns:
            下载结果
        """
        try:
            # 先检查文件大小
            head = requests.head(url, timeout=10)
            content_length = int(head.headers.get('content-length', 0))

            if content_length > self.max_size:
                return {
                    "success": False,
                    "url": url,
                    "error": f"文件过大: {content_length} 字节 (最大 {self.max_size})"
                }

            # 创建目录
            dir_path = os.path.dirname(os.path.abspath(filepath))
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # 下载文件
            response = requests.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            total_size = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)

            return {
                "success": True,
                "url": url,
                "filepath": os.path.abspath(filepath),
                "size": total_size
            }

        except requests.Timeout:
            return {"success": False, "url": url, "error": "下载超时"}
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}

    def download_with_progress(self, url: str, filepath: str,
                               callback=None) -> Dict[str, Any]:
        """带进度回调的下载"""
        try:
            response = requests.get(url, stream=True, timeout=self.timeout)
            total = int(response.headers.get('content-length', 0))

            dir_path = os.path.dirname(os.path.abspath(filepath))
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if callback:
                            callback(downloaded, total)

            return {
                "success": True,
                "url": url,
                "filepath": os.path.abspath(filepath),
                "size": downloaded
            }
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}
