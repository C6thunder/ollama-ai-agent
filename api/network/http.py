#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP 客户端模块
"""

import requests
from typing import Dict, Any, Optional


class HttpClient:
    """HTTP 请求客户端"""

    def __init__(self, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(headers or {
            'User-Agent': 'Mozilla/5.0 (compatible; AI-Agent/1.0)'
        })

    def get(self, url: str, params: Optional[Dict] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """发送 GET 请求"""
        try:
            response = self.session.get(
                url, params=params, headers=headers, timeout=self.timeout
            )
            return self._build_response(response, url)
        except requests.Timeout:
            return {"success": False, "url": url, "error": "请求超时"}
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}

    def post(self, url: str, data: Optional[Dict] = None,
             json_data: Optional[Dict] = None,
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """发送 POST 请求"""
        try:
            response = self.session.post(
                url, data=data, json=json_data, headers=headers, timeout=self.timeout
            )
            return self._build_response(response, url)
        except requests.Timeout:
            return {"success": False, "url": url, "error": "请求超时"}
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}

    def _build_response(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """构建响应结果"""
        is_json = 'application/json' in response.headers.get('Content-Type', '').lower()
        return {
            "success": True,
            "status_code": response.status_code,
            "url": response.url,
            "headers": dict(response.headers),
            "text": response.text,
            "json": response.json() if is_json else None
        }

    def close(self):
        """关闭会话"""
        self.session.close()
