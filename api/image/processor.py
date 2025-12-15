#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像处理模块
"""

import os
from typing import Dict, Any, List, Optional


class ImageProcessor:
    """图像处理器"""

    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']

    def info(self, filepath: str) -> Dict[str, Any]:
        """获取图像信息"""
        try:
            from PIL import Image
            img = Image.open(filepath)
            return {
                "success": True,
                "filepath": filepath,
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height
            }
        except ImportError:
            return {"success": False, "error": "需要安装 Pillow: pip install Pillow"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def resize(self, filepath: str, output_path: str,
               width: int, height: int,
               keep_aspect: bool = True) -> Dict[str, Any]:
        """调整图像大小"""
        try:
            from PIL import Image
            img = Image.open(filepath)

            if keep_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)

            img.save(output_path)
            return {
                "success": True,
                "input": filepath,
                "output": output_path,
                "new_size": img.size
            }
        except ImportError:
            return {"success": False, "error": "需要安装 Pillow"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def convert(self, filepath: str, output_path: str,
                format: str = "JPEG") -> Dict[str, Any]:
        """转换图像格式"""
        try:
            from PIL import Image

            if format.upper() not in self.SUPPORTED_FORMATS:
                return {"success": False, "error": f"不支持的格式: {format}"}

            img = Image.open(filepath)
            if img.mode == 'RGBA' and format.upper() == 'JPEG':
                img = img.convert('RGB')

            img.save(output_path, format=format.upper())
            return {
                "success": True,
                "input": filepath,
                "output": output_path,
                "format": format.upper()
            }
        except ImportError:
            return {"success": False, "error": "需要安装 Pillow"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def compress(self, filepath: str, output_path: str,
                 quality: int = 85) -> Dict[str, Any]:
        """压缩图像"""
        try:
            from PIL import Image
            img = Image.open(filepath)

            if img.mode == 'RGBA':
                img = img.convert('RGB')

            img.save(output_path, optimize=True, quality=quality)

            original_size = os.path.getsize(filepath)
            new_size = os.path.getsize(output_path)

            return {
                "success": True,
                "input": filepath,
                "output": output_path,
                "original_size": original_size,
                "new_size": new_size,
                "compression_ratio": round((1 - new_size / original_size) * 100, 2)
            }
        except ImportError:
            return {"success": False, "error": "需要安装 Pillow"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_images(self, directory: str,
                    extensions: List[str] = None) -> Dict[str, Any]:
        """列出目录中的图像文件"""
        try:
            extensions = extensions or ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            images = []

            for item in os.listdir(directory):
                if any(item.lower().endswith(ext) for ext in extensions):
                    full_path = os.path.join(directory, item)
                    images.append({
                        "name": item,
                        "path": full_path,
                        "size": os.path.getsize(full_path)
                    })

            return {
                "success": True,
                "directory": directory,
                "images": images,
                "count": len(images)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
