"""系统信息工具模块

提供各种系统信息获取和操作功能
包括系统信息、进程管理、网络信息等
"""

import os
import sys
import platform
import socket
import getpass
import subprocess
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# 尝试导入 psutil，如果失败则设为 None
try:
    import psutil
except ImportError:
    psutil = None
    logger.warning("psutil 未安装，系统信息功能将受限")


class SystemUtils:
    """系统信息工具类"""

    @staticmethod
    def get_platform_info() -> Dict[str, str]:
        """获取平台信息

        Returns:
            平台信息字典
        """
        return {
            'system': platform.system(),
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'node': platform.node()
        }

    @staticmethod
    def get_python_info() -> Dict[str, Any]:
        """获取Python信息

        Returns:
            Python信息字典
        """
        return {
            'version': sys.version,
            'version_info': {
                'major': sys.version_info.major,
                'minor': sys.version_info.minor,
                'micro': sys.version_info.micro,
                'releaselevel': sys.version_info.releaselevel
            },
            'executable': sys.executable,
            'path': sys.path,
            'modules': list(sys.modules.keys()),
            'maxsize': sys.maxsize,
            'byteorder': sys.byteorder
        }

    @staticmethod
    def get_current_user() -> Dict[str, str]:
        """获取当前用户信息

        Returns:
            用户信息字典
        """
        return {
            'username': getpass.getuser(),
            'home_dir': os.path.expanduser('~'),
            'current_dir': os.getcwd()
        }

    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """获取CPU信息

        Returns:
            CPU信息字典
        """
        if psutil is None:
            return {
                'count': None,
                'count_logical': None,
                'usage_per_cpu': None,
                'usage_total': None,
                'frequency': None,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
                'error': 'psutil 未安装'
            }

        return {
            'count': psutil.cpu_count(),
            'count_logical': psutil.cpu_count(logical=True),
            'usage_per_cpu': psutil.cpu_percent(percpu=True, interval=1),
            'usage_total': psutil.cpu_percent(interval=1),
            'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }

    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """获取内存信息

        Returns:
            内存信息字典
        """
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'percent': mem.percent,
            'buffers': getattr(mem, 'buffers', 0),
            'cached': getattr(mem, 'cached', 0),
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }

    @staticmethod
    def get_disk_info(path: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取磁盘信息

        Args:
            path: 指定路径，None 表示所有分区

        Returns:
            磁盘信息列表
        """
        if path is None:
            partitions = psutil.disk_partitions()
        else:
            partitions = [psutil.disk_partition(path)]

        disk_info = []
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                })
            except PermissionError:
                logger.warning(f"无法访问磁盘 {partition.device}")

        return disk_info

    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """获取网络信息

        Returns:
            网络信息字典
        """
        # 获取网络接口
        if_addrs = psutil.net_if_addrs()
        if_stats = psutil.net_if_stats()

        interfaces = {}
        for interface_name, addr_list in if_addrs.items():
            interfaces[interface_name] = {
                'addresses': [
                    {
                        'family': addr.family.name if hasattr(addr.family, 'name') else str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    for addr in addr_list
                ],
                'is_up': if_stats[interface_name].isup if interface_name in if_stats else False,
                'speed': if_stats[interface_name].speed if interface_name in if_stats else None
            }

        # 获取网络连接
        connections = []
        for conn in psutil.net_connections():
            connections.append({
                'fd': conn.fd,
                'family': conn.family.name if hasattr(conn.family, 'name') else str(conn.family),
                'type': conn.type.name if hasattr(conn.type, 'name') else str(conn.type),
                'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                'status': conn.status,
                'pid': conn.pid
            })

        return {
            'interfaces': interfaces,
            'connections': connections,
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn()
        }

    @staticmethod
    def get_processes() -> List[Dict[str, Any]]:
        """获取进程列表

        Returns:
            进程信息列表
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return processes

    @staticmethod
    def get_process_by_pid(pid: int) -> Optional[Dict[str, Any]]:
        """根据PID获取进程信息

        Args:
            pid: 进程ID

        Returns:
            进程信息字典
        """
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'create_time': proc.create_time(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'memory_info': proc.memory_info()._asdict(),
                'cmdline': proc.cmdline(),
                'cwd': proc.cwd(),
                'exe': proc.exe(),
                'parent': proc.ppid(),
                'num_threads': proc.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"获取进程信息失败 PID {pid}: {str(e)}")
            return None

    @staticmethod
    def kill_process(pid: int, force: bool = False) -> bool:
        """终止进程

        Args:
            pid: 进程ID
            force: 是否强制终止

        Returns:
            是否成功
        """
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"终止进程失败 PID {pid}: {str(e)}")
            return False

    @staticmethod
    def get_boot_time() -> float:
        """获取系统启动时间

        Returns:
            启动时间戳
        """
        return psutil.boot_time()

    @staticmethod
    def get_uptime() -> float:
        """获取系统运行时间

        Returns:
            运行时间（秒）
        """
        return psutil.boot_time() and (psutil.time.time() - psutil.boot_time())

    @staticmethod
    def get_environment_variables() -> Dict[str, str]:
        """获取环境变量

        Returns:
            环境变量字典
        """
        return dict(os.environ)

    @staticmethod
    def get_variable(name: str, default: Optional[str] = None) -> Optional[str]:
        """获取指定环境变量

        Args:
            name: 变量名
            default: 默认值

        Returns:
            变量值
        """
        return os.environ.get(name, default)

    @staticmethod
    def execute_command(
        command: str,
        shell: bool = True,
        capture_output: bool = True,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """执行系统命令

        Args:
            command: 命令字符串
            shell: 是否使用shell
            capture_output: 是否捕获输出
            timeout: 超时时间（秒）

        Returns:
            命令执行结果
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )

            return {
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else None,
                'stderr': result.stderr if capture_output else None,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            logger.error(f"命令执行超时: {command}")
            return {
                'command': command,
                'returncode': -1,
                'stdout': None,
                'stderr': 'Command timeout',
                'success': False
            }
        except Exception as e:
            logger.error(f"命令执行失败: {str(e)}")
            return {
                'command': command,
                'returncode': -1,
                'stdout': None,
                'stderr': str(e),
                'success': False
            }

    @staticmethod
    def get_load_average() -> Optional[List[float]]:
        """获取系统负载平均值

        Returns:
            1分钟、5分钟、15分钟负载平均值
        """
        if hasattr(os, 'getloadavg'):
            return list(os.getloadavg())
        return None

    @staticmethod
    def get_system_summary() -> Dict[str, Any]:
        """获取系统概要信息

        Returns:
            系统概要信息
        """
        return {
            'platform': SystemUtils.get_platform_info(),
            'python': SystemUtils.get_python_info(),
            'user': SystemUtils.get_current_user(),
            'cpu': SystemUtils.get_cpu_info(),
            'memory': SystemUtils.get_memory_info(),
            'disk': SystemUtils.get_disk_info(),
            'network': SystemUtils.get_network_info(),
            'boot_time': SystemUtils.get_boot_time(),
            'uptime': SystemUtils.get_uptime(),
            'load_average': SystemUtils.get_load_average()
        }

    @staticmethod
    def get_directory_size(dir_path: str) -> int:
        """获取目录大小

        Args:
            dir_path: 目录路径

        Returns:
            目录大小（字节）
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    pass
        return total_size

    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """格式化字节大小

        Args:
            bytes_value: 字节数

        Returns:
            格式化后的字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} EB"

    @staticmethod
    def get_free_port(start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
        """获取可用端口

        Args:
            start_port: 起始端口
            max_attempts: 最大尝试次数

        Returns:
            可用端口号
        """
        import socket
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    continue
        return None

    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """检查端口是否被占用

        Args:
            port: 端口号

        Returns:
            是否被占用
        """
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return False
            except OSError:
                return True

    @staticmethod
    def check_url_reachable(url: str, timeout: float = 5.0) -> bool:
        """检查URL是否可访问

        Args:
            url: URL地址
            timeout: 超时时间（秒）

        Returns:
            是否可访问
        """
        import urllib.request
        import urllib.error

        try:
            urllib.request.urlopen(url, timeout=timeout)
            return True
        except (urllib.error.URLError, socket.timeout):
            return False


# 便捷函数
def get_system_summary() -> Dict[str, Any]:
    """便捷函数：获取系统概要信息"""
    return SystemUtils.get_system_summary()


def format_size(bytes_value: int) -> str:
    """便捷函数：格式化字节大小"""
    return SystemUtils.format_bytes(bytes_value)


def check_port(port: int) -> bool:
    """便捷函数：检查端口是否被占用"""
    return SystemUtils.is_port_in_use(port)


def execute(cmd: str) -> Dict[str, Any]:
    """便捷函数：执行命令"""
    return SystemUtils.execute_command(cmd)


# 使用示例
if __name__ == "__main__":
    # 系统概要信息
    summary = SystemUtils.get_system_summary()
    print("系统概要信息:")
    print(json.dumps(summary, indent=2, default=str))

    # 内存信息
    memory = SystemUtils.get_memory_info()
    print(f"\n总内存: {SystemUtils.format_bytes(memory['total'])}")
    print(f"可用内存: {SystemUtils.format_bytes(memory['available'])}")
    print(f"内存使用率: {memory['percent']:.1f}%")

    # 磁盘信息
    disks = SystemUtils.get_disk_info()
    print("\n磁盘信息:")
    for disk in disks:
        print(f"{disk['device']}: {SystemUtils.format_bytes(disk['used'])} / {SystemUtils.format_bytes(disk['total'])} ({disk['percent']:.1f}%)")

    # CPU信息
    cpu = SystemUtils.get_cpu_info()
    print(f"\nCPU核心数: {cpu['count']}")
    print(f"CPU使用率: {cpu['usage_total']:.1f}%")

    # 运行时间
    uptime = SystemUtils.get_uptime()
    print(f"\n系统运行时间: {uptime / 3600:.1f} 小时")
