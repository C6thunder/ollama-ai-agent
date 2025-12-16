"""验证工具模块

提供各种数据验证和检查功能
包括邮箱验证、URL验证、身份证验证、银行卡验证等
"""

import re
import ipaddress
from typing import Any, Optional, List, Dict, Union, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationUtils:
    """验证工具类"""

    # 常用正则表达式
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    URL_REGEX = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    PHONE_REGEX = re.compile(
        r'^1[3-9]\d{9}$'  # 中国手机号
    )

    ID_CARD_REGEX = re.compile(
        r'^\d{17}[\dXx]$'  # 18位身份证号
    )

    USERNAME_REGEX = re.compile(
        r'^[a-zA-Z0-9_]{3,20}$'  # 3-20位字母数字下划线
    )

    PASSWORD_REGEX = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    )  # 至少8位，包含大小写字母、数字和特殊字符

    IPV4_REGEX = re.compile(
        r'^(\d{1,3}\.){3}\d{1,3}$'
    )

    MAC_REGEX = re.compile(
        r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    )

    @staticmethod
    def is_email(email: str) -> bool:
        """验证邮箱地址

        Args:
            email: 邮箱地址

        Returns:
            是否为有效邮箱
        """
        if not email or len(email) > 254:
            return False
        return bool(ValidationUtils.EMAIL_REGEX.match(email))

    @staticmethod
    def is_url(url: str) -> bool:
        """验证URL

        Args:
            url: URL地址

        Returns:
            是否为有效URL
        """
        if not url or len(url) > 2048:
            return False
        return bool(ValidationUtils.URL_REGEX.match(url))

    @staticmethod
    def is_phone_number(phone: str) -> bool:
        """验证手机号（中国）

        Args:
            phone: 手机号

        Returns:
            是否为有效手机号
        """
        if not phone:
            return False
        return bool(ValidationUtils.PHONE_REGEX.match(phone))

    @staticmethod
    def is_id_card(id_card: str) -> bool:
        """验证身份证号（中国）

        Args:
            id_card: 身份证号

        Returns:
            是否为有效身份证号
        """
        if not id_card or not ValidationUtils.ID_CARD_REGEX.match(id_card):
            return False

        # 验证校验位
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

        # 计算前17位加权值
        checksum = sum(
            int(id_card[i]) * weights[i]
            for i in range(17)
        )

        # 计算校验位
        check_code = check_codes[checksum % 11]
        return check_code == id_card[-1].upper()

    @staticmethod
    def is_ipv4(ip: str) -> bool:
        """验证IPv4地址

        Args:
            ip: IP地址

        Returns:
            是否为有效IPv4
        """
        if not ip or not ValidationUtils.IPV4_REGEX.match(ip):
            return False

        parts = ip.split('.')
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    @staticmethod
    def is_ipv6(ip: str) -> bool:
        """验证IPv6地址

        Args:
            ip: IP地址

        Returns:
            是否为有效IPv6
        """
        try:
            ipaddress.IPv6Address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_mac_address(mac: str) -> bool:
        """验证MAC地址

        Args:
            mac: MAC地址

        Returns:
            是否为有效MAC地址
        """
        if not mac:
            return False
        return bool(ValidationUtils.MAC_REGEX.match(mac))

    @staticmethod
    def is_username(username: str) -> bool:
        """验证用户名

        Args:
            username: 用户名

        Returns:
            是否为有效用户名
        """
        if not username:
            return False
        return bool(ValidationUtils.USERNAME_REGEX.match(username))

    @staticmethod
    def is_strong_password(password: str) -> bool:
        """验证强密码

        Args:
            password: 密码

        Returns:
            是否为强密码
        """
        if not password:
            return False
        return bool(ValidationUtils.PASSWORD_REGEX.match(password))

    @staticmethod
    def is_number(value: Any) -> bool:
        """验证是否为数字

        Args:
            value: 要验证的值

        Returns:
            是否为数字
        """
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_integer(value: Any) -> bool:
        """验证是否为整数

        Args:
            value: 要验证的值

        Returns:
            是否为整数
        """
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_float(value: Any) -> bool:
        """验证是否为浮点数

        Args:
            value: 要验证的值

        Returns:
            是否为浮点数
        """
        try:
            float(value)
            return isinstance(value, float) or '.' in str(value)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_alpha(text: str) -> bool:
        """验证是否只包含字母

        Args:
            text: 文本

        Returns:
            是否只包含字母
        """
        return text.isalpha() if text else False

    @staticmethod
    def is_alphanumeric(text: str) -> bool:
        """验证是否只包含字母和数字

        Args:
            text: 文本

        Returns:
            是否只包含字母和数字
        """
        return text.isalnum() if text else False

    @staticmethod
    def is_alpha_numeric_underscore(text: str) -> bool:
        """验证是否只包含字母、数字和下划线

        Args:
            text: 文本

        Returns:
            是否只包含字母、数字和下划线
        """
        return bool(re.match(r'^[a-zA-Z0-9_]+$', text)) if text else False

    @staticmethod
    def has_special_chars(text: str) -> bool:
        """检查是否包含特殊字符

        Args:
            text: 文本

        Returns:
            是否包含特殊字符
        """
        return bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', text)) if text else False

    @staticmethod
    def has_uppercase(text: str) -> bool:
        """检查是否包含大写字母

        Args:
            text: 文本

        Returns:
            是否包含大写字母
        """
        return any(c.isupper() for c in text) if text else False

    @staticmethod
    def has_lowercase(text: str) -> bool:
        """检查是否包含小写字母

        Args:
            text: 文本

        Returns:
            是否包含小写字母
        """
        return any(c.islower() for c in text) if text else False

    @staticmethod
    def has_digit(text: str) -> bool:
        """检查是否包含数字

        Args:
            text: 文本

        Returns:
            是否包含数字
        """
        return any(c.isdigit() for c in text) if text else False

    @staticmethod
    def in_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> bool:
        """检查值是否在范围内

        Args:
            value: 要检查的值
            min_val: 最小值
            max_val: 最大值

        Returns:
            是否在范围内
        """
        try:
            return min_val <= float(value) <= max_val
        except (ValueError, TypeError):
            return False

    @staticmethod
    def min_length(text: str, min_len: int) -> bool:
        """检查最小长度

        Args:
            text: 文本
            min_len: 最小长度

        Returns:
            是否满足最小长度
        """
        return len(text) >= min_len if text else False

    @staticmethod
    def max_length(text: str, max_len: int) -> bool:
        """检查最大长度

        Args:
            text: 文本
            max_len: 最大长度

        Returns:
            是否满足最大长度
        """
        return len(text) <= max_len if text else False

    @staticmethod
    def length_in_range(text: str, min_len: int, max_len: int) -> bool:
        """检查长度是否在范围内

        Args:
            text: 文本
            min_len: 最小长度
            max_len: 最大长度

        Returns:
            长度是否在范围内
        """
        return min_len <= len(text) <= max_len if text else False

    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """验证是否为有效JSON

        Args:
            json_str: JSON字符串

        Returns:
            是否为有效JSON
        """
        import json
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def is_valid_date(date_str: str, format_str: str = '%Y-%m-%d') -> bool:
        """验证是否为有效日期

        Args:
            date_str: 日期字符串
            format_str: 日期格式

        Returns:
            是否为有效日期
        """
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_in_list(value: Any, valid_list: List[Any]) -> bool:
        """检查值是否在列表中

        Args:
            value: 要检查的值
            valid_list: 有效值列表

        Returns:
            是否在列表中
        """
        return value in valid_list

    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """检查值是否不为空

        Args:
            value: 要检查的值

        Returns:
            是否不为空
        """
        if value is None:
            return False
        if isinstance(value, str):
            return len(value.strip()) > 0
        if isinstance(value, (list, dict, tuple)):
            return len(value) > 0
        return True

    @staticmethod
    def is_unique_list(values: List[Any]) -> bool:
        """检查列表中的值是否唯一

        Args:
            values: 值列表

        Returns:
            是否所有值都唯一
        """
        return len(values) == len(set(values)) if values else True

    @staticmethod
    def matches_regex(text: str, pattern: str) -> bool:
        """检查文本是否匹配正则表达式

        Args:
            text: 文本
            pattern: 正则表达式模式

        Returns:
            是否匹配
        """
        try:
            return bool(re.match(pattern, text))
        except re.error:
            return False

    @staticmethod
    def contains_regex(text: str, pattern: str) -> bool:
        """检查文本是否包含匹配正则表达式的子串

        Args:
            text: 文本
            pattern: 正则表达式模式

        Returns:
            是否包含匹配的子串
        """
        try:
            return bool(re.search(pattern, text))
        except re.error:
            return False

    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """检查文件名是否安全

        Args:
            filename: 文件名

        Returns:
            是否为安全文件名
        """
        if not filename:
            return False

        # 检查危险字符
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in filename for char in dangerous_chars):
            return False

        # 检查保留名称
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            return False

        return True

    @staticmethod
    def is_sql_injection_safe(text: str) -> bool:
        """检查文本是否安全（防SQL注入）

        Args:
            text: 文本

        Returns:
            是否安全
        """
        if not text:
            return True

        # 检查危险SQL关键字
        sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'EXEC', 'EXECUTE', 'UNION', 'SCRIPT', 'OR', 'AND'
        ]

        text_upper = text.upper()
        return not any(keyword in text_upper for keyword in sql_keywords)

    @staticmethod
    def is_xss_safe(text: str) -> bool:
        """检查文本是否安全（防XSS）

        Args:
            text: 文本

        Returns:
            是否安全
        """
        if not text:
            return True

        # 检查危险标签和脚本
        xss_patterns = [
            r'<script[^>]*>.*?</script>',  # script标签
            r'javascript:',  # javascript协议
            r'on\w+\s*=',  # 事件处理器
            r'<iframe[^>]*>.*?</iframe>',  # iframe标签
            r'<object[^>]*>.*?</object>',  # object标签
            r'<embed[^>]*>.*?</embed>',  # embed标签
        ]

        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                return False

        return True

    @staticmethod
    def validate_with_custom_rule(value: Any, rule: Callable[[Any], bool], error_msg: str = "验证失败") -> tuple[bool, str]:
        """使用自定义规则验证

        Args:
            value: 要验证的值
            rule: 验证规则函数
            error_msg: 错误消息

        Returns:
            (是否通过, 错误消息)
        """
        try:
            if rule(value):
                return True, ""
            return False, error_msg
        except Exception as e:
            return False, f"验证过程中发生错误: {str(e)}"

    @staticmethod
    def batch_validate(validations: List[tuple]) -> Dict[str, Any]:
        """批量验证

        Args:
            validations: 验证规则列表，每个元素为 (验证函数, 值, 字段名)

        Returns:
            验证结果
        """
        results = {
            'valid': True,
            'errors': {},
            'field_results': {}
        }

        for validation in validations:
            if len(validation) == 3:
                rule, value, field_name = validation
                valid, error_msg = ValidationUtils.validate_with_custom_rule(value, rule)
                results['field_results'][field_name] = {
                    'valid': valid,
                    'error': error_msg if not valid else None
                }
                if not valid:
                    results['valid'] = False
                    results['errors'][field_name] = error_msg

        return results


# 便捷函数
def is_valid_email(email: str) -> bool:
    """便捷函数：验证邮箱"""
    return ValidationUtils.is_email(email)


def is_valid_url(url: str) -> bool:
    """便捷函数：验证URL"""
    return ValidationUtils.is_url(url)


def is_valid_phone(phone: str) -> bool:
    """便捷函数：验证手机号"""
    return ValidationUtils.is_phone_number(phone)


def is_valid_id_card(id_card: str) -> bool:
    """便捷函数：验证身份证"""
    return ValidationUtils.is_id_card(id_card)


def is_valid_password(password: str) -> bool:
    """便捷函数：验证密码强度"""
    return ValidationUtils.is_strong_password(password)


# 使用示例
if __name__ == "__main__":
    # 验证邮箱
    emails = ['test@example.com', 'invalid-email', 'user@domain.co.uk']
    for email in emails:
        print(f"{email}: {ValidationUtils.is_email(email)}")

    # 验证URL
    urls = ['https://www.google.com', 'invalid-url', 'http://example.org']
    for url in urls:
        print(f"{url}: {ValidationUtils.is_url(url)}")

    # 验证手机号
    phones = ['13812345678', '12345678901', 'invalid-phone']
    for phone in phones:
        print(f"{phone}: {ValidationUtils.is_phone_number(phone)}")

    # 验证密码强度
    passwords = ['StrongPass123!', 'weak', 'MediumPass1', 'StrongPass@123']
    for pwd in passwords:
        print(f"{pwd}: {ValidationUtils.is_strong_password(pwd)}")

    # 批量验证
    user_data = {
        'email': 'user@example.com',
        'phone': '13812345678',
        'username': 'john_doe',
        'age': 25
    }

    validations = [
        (ValidationUtils.is_email, user_data['email'], 'email'),
        (ValidationUtils.is_phone_number, user_data['phone'], 'phone'),
        (ValidationUtils.is_username, user_data['username'], 'username'),
        (lambda x: ValidationUtils.in_range(x, 0, 120), user_data['age'], 'age')
    ]

    results = ValidationUtils.batch_validate(validations)
    print(f"\n批量验证结果:")
    print(json.dumps(results, indent=2, default=str))
