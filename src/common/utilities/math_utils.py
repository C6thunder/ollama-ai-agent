"""数学工具模块

提供各种数学计算功能
包括基础运算、统计、几何、代数等
"""

import math
import statistics
from typing import List, Union, Tuple, Dict, Any
from functools import lru_cache


class MathUtils:
    """数学计算工具类"""

    @staticmethod
    def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """加法运算"""
        return a + b

    @staticmethod
    def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """减法运算"""
        return a - b

    @staticmethod
    def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """乘法运算"""
        return a * b

    @staticmethod
    def divide(a: Union[int, float], b: Union[int, float]) -> float:
        """除法运算"""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b

    @staticmethod
    def power(base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
        """幂运算"""
        return base ** exponent

    @staticmethod
    def sqrt(value: Union[int, float]) -> float:
        """平方根"""
        return math.sqrt(value)

    @staticmethod
    def abs(value: Union[int, float]) -> Union[int, float]:
        """绝对值"""
        return abs(value)

    @staticmethod
    def round(value: Union[int, float], digits: int = 0) -> float:
        """四舍五入"""
        return round(value, digits)

    @staticmethod
    def floor(value: Union[int, float]) -> int:
        """向下取整"""
        return math.floor(value)

    @staticmethod
    def ceil(value: Union[int, float]) -> int:
        """向上取整"""
        return math.ceil(value)

    @staticmethod
    def factorial(n: int) -> int:
        """阶乘"""
        return math.factorial(n)

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """最大公约数"""
        return math.gcd(a, b)

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """最小公倍数"""
        return abs(a * b) // math.gcd(a, b)

    @staticmethod
    def sin(angle: Union[int, float]) -> float:
        """正弦函数（弧度）"""
        return math.sin(angle)

    @staticmethod
    def cos(angle: Union[int, float]) -> float:
        """余弦函数（弧度）"""
        return math.cos(angle)

    @staticmethod
    def tan(angle: Union[int, float]) -> float:
        """正切函数（弧度）"""
        return math.tan(angle)

    @staticmethod
    def log(value: Union[int, float], base: Union[int, float] = math.e) -> float:
        """对数运算"""
        return math.log(value, base)

    @staticmethod
    def log10(value: Union[int, float]) -> float:
        """常用对数（以10为底）"""
        return math.log10(value)

    @staticmethod
    def mean(numbers: List[Union[int, float]]) -> float:
        """计算平均值"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        return statistics.mean(numbers)

    @staticmethod
    def median(numbers: List[Union[int, float]]) -> float:
        """计算中位数"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        return statistics.median(numbers)

    @staticmethod
    def mode(numbers: List[Union[int, float]]) -> Union[float, List[float]]:
        """计算众数"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        return statistics.mode(numbers) if len(set(numbers)) == len(numbers) else statistics.multimode(numbers)

    @staticmethod
    def stdev(numbers: List[Union[int, float]]) -> float:
        """计算标准差"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        return statistics.stdev(numbers)

    @staticmethod
    def variance(numbers: List[Union[int, float]]) -> float:
        """计算方差"""
        if not numbers:
            raise ValueError("数字列表不能为空")
        return statistics.variance(numbers)

    @staticmethod
    def percentile(numbers: List[Union[int, float]], p: float) -> float:
        """计算百分位数

        Args:
            numbers: 数字列表
            p: 百分位数（0-100）

        Returns:
            对应的百分位数值
        """
        if not numbers:
            raise ValueError("数字列表不能为空")
        if not 0 <= p <= 100:
            raise ValueError("百分位数必须在0-100之间")
        return statistics.quantiles(numbers, n=100)[int(p) - 1]

    @staticmethod
    def correlation(x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
        """计算相关系数"""
        if len(x) != len(y):
            raise ValueError("两个列表长度必须相同")
        if not x:
            raise ValueError("列表不能为空")
        return statistics.correlation(x, y)

    @staticmethod
    def linear_regression(x: List[Union[int, float]], y: List[Union[int, float]]) -> Dict[str, float]:
        """线性回归

        Returns:
            包含斜率和截距的字典
        """
        if len(x) != len(y):
            raise ValueError("两个列表长度必须相同")
        if not x:
            raise ValueError("列表不能为空")

        slope, intercept = statistics.linear_regression(x, y)
        return {"slope": slope, "intercept": intercept}

    @staticmethod
    def combinations(n: int, r: int) -> int:
        """计算组合数 C(n, r)"""
        return math.comb(n, r)

    @staticmethod
    def permutations(n: int, r: int) -> int:
        """计算排列数 P(n, r)"""
        return math.perm(n, r)

    @staticmethod
    def is_prime(n: int) -> bool:
        """判断是否为素数"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True

    @staticmethod
    def fibonacci(n: int) -> List[int]:
        """生成斐波那契数列

        Args:
            n: 数列长度

        Returns:
            斐波那契数列列表
        """
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        elif n == 2:
            return [0, 1]

        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i - 1] + fib[i - 2])
        return fib

    @staticmethod
    def convert_base(number: int, base: int) -> str:
        """将数字转换为指定进制

        Args:
            number: 要转换的数字
            base: 目标进制（2-36）

        Returns:
            转换后的字符串
        """
        if base < 2 or base > 36:
            raise ValueError("进制必须在2-36之间")
        if number == 0:
            return "0"

        result = ""
        is_negative = number < 0
        number = abs(number)

        while number > 0:
            remainder = number % base
            if remainder < 10:
                result = str(remainder) + result
            else:
                result = chr(ord('A') + remainder - 10) + result
            number //= base

        return ("-" if is_negative else "") + result

    @staticmethod
    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """计算两点间距离"""
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    @staticmethod
    def area_circle(radius: float) -> float:
        """计算圆形面积"""
        return math.pi * radius ** 2

    @staticmethod
    def circumference(radius: float) -> float:
        """计算圆形周长"""
        return 2 * math.pi * radius

    @staticmethod
    def area_rectangle(length: float, width: float) -> float:
        """计算矩形面积"""
        return length * width

    @staticmethod
    def area_triangle(base: float, height: float) -> float:
        """计算三角形面积"""
        return 0.5 * base * height

    @staticmethod
    def volume_sphere(radius: float) -> float:
        """计算球体体积"""
        return (4 / 3) * math.pi * radius ** 3

    @staticmethod
    def volume_cube(side: float) -> float:
        """计算立方体体积"""
        return side ** 3

    @staticmethod
    def volume_cylinder(radius: float, height: float) -> float:
        """计算圆柱体体积"""
        return math.pi * radius ** 2 * height

    @staticmethod
    @lru_cache(maxsize=128)
    def is_even(n: int) -> bool:
        """判断是否为偶数（带缓存）"""
        return n % 2 == 0

    @staticmethod
    @lru_cache(maxsize=128)
    def is_odd(n: int) -> bool:
        """判断是否为奇数（带缓存）"""
        return n % 2 == 1


# 便捷函数
def calculate(operation: str, *args) -> Any:
    """便捷计算函数

    Args:
        operation: 运算类型（add, subtract, multiply, divide, power, sqrt等）
        *args: 运算参数

    Returns:
        计算结果
    """
    method = getattr(MathUtils, operation, None)
    if not method:
        raise ValueError(f"不支持的运算类型: {operation}")
    return method(*args)


# 使用示例
if __name__ == "__main__":
    # 基础运算
    print(f"10 + 5 = {MathUtils.add(10, 5)}")
    print(f"10 - 5 = {MathUtils.subtract(10, 5)}")
    print(f"10 * 5 = {MathUtils.multiply(10, 5)}")
    print(f"10 / 5 = {MathUtils.divide(10, 5)}")

    # 高级运算
    print(f"2^10 = {MathUtils.power(2, 10)}")
    print(f"√16 = {MathUtils.sqrt(16)}")
    print(f"10! = {MathUtils.factorial(10)}")

    # 统计运算
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"平均值: {MathUtils.mean(numbers)}")
    print(f"中位数: {MathUtils.median(numbers)}")
    print(f"标准差: {MathUtils.stdev(numbers)}")

    # 几何计算
    print(f"圆的面积 (r=5): {MathUtils.area_circle(5):.2f}")
    print(f"球的体积 (r=5): {MathUtils.volume_sphere(5):.2f}")
