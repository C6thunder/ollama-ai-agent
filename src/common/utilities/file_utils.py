"""文件处理工具模块

提供各种文件操作和处理的工具函数
包括文件读写、目录操作、文件类型检测、压缩等
"""

import os
import json
import csv
import gzip
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, BinaryIO, TextIO
import logging

logger = logging.getLogger(__name__)


class FileUtils:
    """文件处理工具类"""

    # 常见文件扩展名映射
    FILE_EXTENSIONS = {
        '.txt': '文本文件',
        '.md': 'Markdown文档',
        '.py': 'Python脚本',
        '.js': 'JavaScript文件',
        '.html': 'HTML网页',
        '.css': 'CSS样式表',
        '.json': 'JSON数据文件',
        '.xml': 'XML文件',
        '.csv': 'CSV数据文件',
        '.yaml': 'YAML配置文件',
        '.yml': 'YAML配置文件',
        '.jpg': 'JPEG图像',
        '.jpeg': 'JPEG图像',
        '.png': 'PNG图像',
        '.gif': 'GIF图像',
        '.pdf': 'PDF文档',
        '.doc': 'Word文档',
        '.docx': 'Word文档',
        '.xls': 'Excel表格',
        '.xlsx': 'Excel表格',
        '.ppt': 'PowerPoint演示',
        '.pptx': 'PowerPoint演示',
        '.zip': 'ZIP压缩包',
        '.tar': 'TAR压缩包',
        '.gz': 'GZIP压缩文件'
    }

    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> str:
        """读取文本文件

        Args:
            file_path: 文件路径
            encoding: 编码格式

        Returns:
            文件内容
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def write_file(
        file_path: str,
        content: str,
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> None:
        """写入文本文件

        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 编码格式
            create_dirs: 是否自动创建目录
        """
        try:
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def read_json(file_path: str, encoding: str = 'utf-8') -> Dict[Any, Any]:
        """读取JSON文件

        Args:
            file_path: 文件路径
            encoding: 编码格式

        Returns:
            JSON数据
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取JSON文件失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def write_json(
        file_path: str,
        data: Dict[Any, Any],
        indent: int = 2,
        encoding: str = 'utf-8',
        ensure_ascii: bool = False
    ) -> None:
        """写入JSON文件

        Args:
            file_path: 文件路径
            data: 要写入的数据
            indent: 缩进空格数
            encoding: 编码格式
            ensure_ascii: 是否使用ASCII编码
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        except Exception as e:
            logger.error(f"写入JSON文件失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def read_csv(file_path: str, encoding: str = 'utf-8') -> List[Dict[str, str]]:
        """读取CSV文件

        Args:
            file_path: 文件路径
            encoding: 编码格式

        Returns:
            CSV数据列表
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"读取CSV文件失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def write_csv(
        file_path: str,
        data: List[Dict[str, Any]],
        encoding: str = 'utf-8'
    ) -> None:
        """写入CSV文件

        Args:
            file_path: 文件路径
            data: 要写入的数据
            encoding: 编码格式
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if not data:
                return

            with open(file_path, 'w', encoding=encoding, newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            logger.error(f"写入CSV文件失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def copy_file(src: str, dst: str, create_dirs: bool = True) -> None:
        """复制文件

        Args:
            src: 源文件路径
            dst: 目标文件路径
            create_dirs: 是否创建目标目录
        """
        try:
            if create_dirs:
                os.makedirs(os.path.dirname(dst), exist_ok=True)

            shutil.copy2(src, dst)
        except Exception as e:
            logger.error(f"复制文件失败 {src} -> {dst}: {str(e)}")
            raise

    @staticmethod
    def move_file(src: str, dst: str, create_dirs: bool = True) -> None:
        """移动文件

        Args:
            src: 源文件路径
            dst: 目标文件路径
            create_dirs: 是否创建目标目录
        """
        try:
            if create_dirs:
                os.makedirs(os.path.dirname(dst), exist_ok=True)

            shutil.move(src, dst)
        except Exception as e:
            logger.error(f"移动文件失败 {src} -> {dst}: {str(e)}")
            raise

    @staticmethod
    def delete_file(file_path: str) -> None:
        """删除文件

        Args:
            file_path: 文件路径
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"删除文件失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def create_directory(dir_path: str) -> None:
        """创建目录

        Args:
            dir_path: 目录路径
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            logger.error(f"创建目录失败 {dir_path}: {str(e)}")
            raise

    @staticmethod
    def delete_directory(dir_path: str) -> None:
        """删除目录

        Args:
            dir_path: 目录路径
        """
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        except Exception as e:
            logger.error(f"删除目录失败 {dir_path}: {str(e)}")
            raise

    @staticmethod
    def list_files(
        dir_path: str,
        recursive: bool = False,
        include_dirs: bool = False,
        pattern: Optional[str] = None
    ) -> List[str]:
        """列出文件

        Args:
            dir_path: 目录路径
            recursive: 是否递归查找
            include_dirs: 是否包含目录
            pattern: 文件名模式（支持通配符）

        Returns:
            文件路径列表
        """
        try:
            if not os.path.exists(dir_path):
                return []

            import fnmatch

            files = []
            if recursive:
                for root, dirs, filenames in os.walk(dir_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        if include_dirs and os.path.isdir(file_path):
                            files.append(file_path)
                        if pattern is None or fnmatch.fnmatch(filename, pattern):
                            files.append(file_path)
            else:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        if pattern is None or fnmatch.fnmatch(item, pattern):
                            files.append(item_path)
                    elif include_dirs:
                        files.append(item_path)

            return files
        except Exception as e:
            logger.error(f"列出文件失败 {dir_path}: {str(e)}")
            raise

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            文件大小（字节）
        """
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"获取文件大小失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名

        Args:
            file_path: 文件路径

        Returns:
            文件扩展名（小写）
        """
        return Path(file_path).suffix.lower()

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """获取文件类型描述

        Args:
            file_path: 文件路径

        Returns:
            文件类型描述
        """
        ext = FileUtils.get_file_extension(file_path)
        return FileUtils.FILE_EXTENSIONS.get(ext, '未知类型')

    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """获取MIME类型

        Args:
            file_path: 文件路径

        Returns:
            MIME类型
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

    @staticmethod
    def calculate_md5(file_path: str, chunk_size: int = 8192) -> str:
        """计算文件MD5值

        Args:
            file_path: 文件路径
            chunk_size: 读取块大小

        Returns:
            MD5哈希值
        """
        try:
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b''):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            logger.error(f"计算MD5失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def calculate_sha256(file_path: str, chunk_size: int = 8192) -> str:
        """计算文件SHA256值

        Args:
            file_path: 文件路径
            chunk_size: 读取块大小

        Returns:
            SHA256哈希值
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b''):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"计算SHA256失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def compress_file(src: str, dst: str) -> None:
        """压缩文件（gzip）

        Args:
            src: 源文件路径
            dst: 目标压缩文件路径
        """
        try:
            with open(src, 'rb') as f_in:
                with gzip.open(dst, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            logger.error(f"压缩文件失败 {src} -> {dst}: {str(e)}")
            raise

    @staticmethod
    def decompress_file(src: str, dst: str) -> None:
        """解压缩文件（gzip）

        Args:
            src: 源压缩文件路径
            dst: 目标文件路径
        """
        try:
            with gzip.open(src, 'rb') as f_in:
                with open(dst, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            logger.error(f"解压缩文件失败 {src} -> {dst}: {str(e)}")
            raise

    @staticmethod
    def archive_directory(src_dir: str, dst_archive: str) -> None:
        """创建目录压缩包

        Args:
            src_dir: 源目录路径
            dst_archive: 目标压缩包路径
        """
        try:
            archive_format = Path(dst_archive).suffix.lower()
            if archive_format == '.zip':
                shutil.make_archive(
                    dst_archive[:-4],  # 去掉.zip后缀
                    'zip',
                    src_dir
                )
            elif archive_format in ['.tar', '.tar.gz', '.tgz']:
                shutil.make_archive(
                    dst_archive[:-7] if archive_format in ['.tar.gz', '.tgz'] else dst_archive[:-4],
                    'gztar' if archive_format in ['.tar.gz', '.tgz'] else 'tar',
                    src_dir
                )
            else:
                raise ValueError(f"不支持的压缩格式: {archive_format}")
        except Exception as e:
            logger.error(f"创建压缩包失败 {src_dir} -> {dst_archive}: {str(e)}")
            raise

    @staticmethod
    def extract_archive(archive: str, dst_dir: str) -> None:
        """解压缩包

        Args:
            archive: 压缩包路径
            dst_dir: 目标目录路径
        """
        try:
            os.makedirs(dst_dir, exist_ok=True)

            shutil.unpack_archive(archive, dst_dir)
        except Exception as e:
            logger.error(f"解压缩失败 {archive} -> {dst_dir}: {str(e)}")
            raise

    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            文件信息字典
        """
        try:
            stat = os.stat(file_path)
            info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'extension': FileUtils.get_file_extension(file_path),
                'type': FileUtils.get_file_type(file_path),
                'mime_type': FileUtils.get_mime_type(file_path),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime
            }
            return info
        except Exception as e:
            logger.error(f"获取文件信息失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def find_files(
        search_path: str,
        name_pattern: Optional[str] = None,
        extension: Optional[str] = None,
        max_results: int = 100
    ) -> List[str]:
        """查找文件

        Args:
            search_path: 搜索路径
            name_pattern: 文件名模式
            extension: 文件扩展名
            max_results: 最大结果数

        Returns:
            匹配的文件路径列表
        """
        try:
            files = []
            for root, _, filenames in os.walk(search_path):
                for filename in filenames:
                    # 检查扩展名
                    if extension and not filename.lower().endswith(extension.lower()):
                        continue

                    # 检查名称模式
                    if name_pattern:
                        import fnmatch
                        if not fnmatch.fnmatch(filename, name_pattern):
                            continue

                    files.append(os.path.join(root, filename))

                    if len(files) >= max_results:
                        return files

            return files
        except Exception as e:
            logger.error(f"查找文件失败 {search_path}: {str(e)}")
            raise

    @staticmethod
    def is_binary_file(file_path: str, chunk_size: int = 1024) -> bool:
        """判断是否为二进制文件

        Args:
            file_path: 文件路径
            chunk_size: 读取块大小

        Returns:
            是否为二进制文件
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(chunk_size)
                # 检查是否包含空字节
                return b'\0' in chunk
        except Exception as e:
            logger.error(f"判断文件类型失败 {file_path}: {str(e)}")
            raise

    @staticmethod
    def get_directory_size(dir_path: str) -> int:
        """获取目录总大小

        Args:
            dir_path: 目录路径

        Returns:
            目录总大小（字节）
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size
        except Exception as e:
            logger.error(f"获取目录大小失败 {dir_path}: {str(e)}")
            raise


# 便捷函数
def read_text(file_path: str) -> str:
    """便捷函数：读取文本文件"""
    return FileUtils.read_file(file_path)


def write_text(file_path: str, content: str) -> None:
    """便捷函数：写入文本文件"""
    FileUtils.write_file(file_path, content)


def read_json_data(file_path: str) -> Dict[Any, Any]:
    """便捷函数：读取JSON文件"""
    return FileUtils.read_json(file_path)


def write_json_data(file_path: str, data: Dict[Any, Any]) -> None:
    """便捷函数：写入JSON文件"""
    FileUtils.write_json(file_path, data)


def get_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """便捷函数：获取文件哈希值"""
    if algorithm.lower() == 'md5':
        return FileUtils.calculate_md5(file_path)
    elif algorithm.lower() == 'sha256':
        return FileUtils.calculate_sha256(file_path)
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")


# 使用示例
if __name__ == "__main__":
    # 文件操作
    print("文件操作示例:")
    FileUtils.write_file('test.txt', 'Hello, World!')
    content = FileUtils.read_file('test.txt')
    print(f"读取内容: {content}")

    # JSON操作
    data = {'name': 'Alice', 'age': 30, 'city': 'Beijing'}
    FileUtils.write_json('test.json', data)
    loaded_data = FileUtils.read_json('test.json')
    print(f"JSON数据: {loaded_data}")

    # 文件信息
    info = FileUtils.get_file_info('test.txt')
    print(f"文件信息: {json.dumps(info, indent=2)}")

    # 清理测试文件
    FileUtils.delete_file('test.txt')
    FileUtils.delete_file('test.json')
