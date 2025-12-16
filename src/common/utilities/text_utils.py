"""文本处理工具模块

提供各种文本处理和操作功能
包括文本清洗、转换、格式化、提取等
"""

import re
import html
import unicodedata
from typing import List, Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class TextUtils:
    """文本处理工具类"""

    @staticmethod
    def to_lowercase(text: str) -> str:
        """转换为小写

        Args:
            text: 输入文本

        Returns:
            小写文本
        """
        return text.lower() if text else ""

    @staticmethod
    def to_uppercase(text: str) -> str:
        """转换为大写

        Args:
            text: 输入文本

        Returns:
            大写文本
        """
        return text.upper() if text else ""

    @staticmethod
    def to_title_case(text: str) -> str:
        """转换为标题格式

        Args:
            text: 输入文本

        Returns:
            标题格式文本
        """
        return text.title() if text else ""

    @staticmethod
    def to_capitalize(text: str) -> str:
        """首字母大写

        Args:
            text: 输入文本

        Returns:
            首字母大写的文本
        """
        return text.capitalize() if text else ""

    @staticmethod
    def strip(text: str) -> str:
        """去除首尾空白

        Args:
            text: 输入文本

        Returns:
            去除空白后的文本
        """
        return text.strip() if text else ""

    @staticmethod
    def remove_whitespace(text: str) -> str:
        """去除所有空白字符

        Args:
            text: 输入文本

        Returns:
            去除空白后的文本
        """
        return re.sub(r'\s+', '', text) if text else ""

    @staticmethod
    def collapse_whitespace(text: str) -> str:
        """折叠空白字符（将多个空白合并为一个）

        Args:
            text: 输入文本

        Returns:
            折叠空白后的文本
        """
        return re.sub(r'\s+', ' ', text) if text else ""

    @staticmethod
    def remove_punctuation(text: str) -> str:
        """去除标点符号

        Args:
            text: 输入文本

        Returns:
            去除标点符号后的文本
        """
        import string
        return text.translate(str.maketrans('', '', string.punctuation)) if text else ""

    @staticmethod
    def remove_digits(text: str) -> str:
        """去除数字

        Args:
            text: 输入文本

        Returns:
            去除数字后的文本
        """
        return re.sub(r'\d+', '', text) if text else ""

    @staticmethod
    def remove_special_chars(text: str, keep_spaces: bool = True) -> str:
        """去除特殊字符

        Args:
            text: 输入文本
            keep_spaces: 是否保留空格

        Returns:
            去除特殊字符后的文本
        """
        if keep_spaces:
            return re.sub(r'[^a-zA-Z0-9\s]', '', text) if text else ""
        else:
            return re.sub(r'[^a-zA-Z0-9]', '', text) if text else ""

    @staticmethod
    def escape_html(text: str) -> str:
        """转义HTML

        Args:
            text: 输入文本

        Returns:
            转义后的文本
        """
        return html.escape(text) if text else ""

    @staticmethod
    def unescape_html(text: str) -> str:
        """反转义HTML

        Args:
            text: 输入文本

        Returns:
            反转义后的文本
        """
        return html.unescape(text) if text else ""

    @staticmethod
    def normalize_unicode(text: str, form: str = 'NFKC') -> str:
        """Unicode标准化

        Args:
            text: 输入文本
            form: 标准化形式（NFKC, NFC, NFKD, NFD）

        Returns:
            标准化后的文本
        """
        return unicodedata.normalize(form, text) if text else ""

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """截断文本

        Args:
            text: 输入文本
            max_length: 最大长度
            suffix: 截断后缀

        Returns:
            截断后的文本
        """
        if not text or len(text) <= max_length:
            return text or ""
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def wrap_text(text: str, width: int = 80) -> List[str]:
        """文本换行

        Args:
            text: 输入文本
            width: 行宽

        Returns:
            换行后的文本行列表
        """
        if not text:
            return []

        import textwrap
        return textwrap.wrap(text, width)

    @staticmethod
    def word_count(text: str) -> int:
        """统计单词数

        Args:
            text: 输入文本

        Returns:
            单词数
        """
        if not text:
            return 0
        return len(re.findall(r'\b\w+\b', text))

    @staticmethod
    def char_count(text: str, include_spaces: bool = True) -> int:
        """统计字符数

        Args:
            text: 输入文本
            include_spaces: 是否包含空格

        Returns:
            字符数
        """
        if not text:
            return 0
        return len(text) if include_spaces else len(text.replace(' ', ''))

    @staticmethod
    def line_count(text: str) -> int:
        """统计行数

        Args:
            text: 输入文本

        Returns:
            行数
        """
        if not text:
            return 0
        return len(text.splitlines())

    @staticmethod
    def paragraph_count(text: str) -> int:
        """统计段落数

        Args:
            text: 输入文本

        Returns:
            段落数
        """
        if not text:
            return 0
        return len([p for p in text.split('\n\n') if p.strip()])

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """提取邮箱地址

        Args:
            text: 输入文本

        Returns:
            邮箱地址列表
        """
        if not text:
            return []

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """提取URL

        Args:
            text: 输入文本

        Returns:
            URL列表
        """
        if not text:
            return []

        url_pattern = r'https?://[^\s]+'
        return re.findall(url_pattern, text)

    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """提取手机号（中国）

        Args:
            text: 输入文本

        Returns:
            手机号列表
        """
        if not text:
            return []

        phone_pattern = r'1[3-9]\d{9}'
        return re.findall(phone_pattern, text)

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """提取标签

        Args:
            text: 输入文本

        Returns:
            标签列表
        """
        if not text:
            return []

        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, text)

    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """提取@提及

        Args:
            text: 输入文本

        Returns:
            @提及列表
        """
        if not text:
            return []

        mention_pattern = r'@\w+'
        return re.findall(mention_pattern, text)

    @staticmethod
    def replace_pattern(text: str, pattern: str, replacement: str) -> str:
        """替换模式

        Args:
            text: 输入文本
            pattern: 正则表达式模式
            replacement: 替换文本

        Returns:
            替换后的文本
        """
        if not text:
            return ""
        return re.sub(pattern, replacement, text)

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        """分割句子

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        if not text:
            return []

        # 简单句子分割（按句号、问号、感叹号分割）
        sentence_pattern = r'[.!?。！？]+'
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def split_paragraphs(text: str) -> List[str]:
        """分割段落

        Args:
            text: 输入文本

        Returns:
            段落列表
        """
        if not text:
            return []

        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]

    @staticmethod
    def slugify(text: str, lowercase: bool = True) -> str:
        """转换为URL友好的slug

        Args:
            text: 输入文本
            lowercase: 是否转为小写

        Returns:
            slug字符串
        """
        if not text:
            return ""

        # 转换为小写
        text = text.lower() if lowercase else text

        # 替换特殊字符为连字符
        text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)

        # 折叠空白
        text = re.sub(r'\s+', '-', text)

        # 去除首尾连字符
        return text.strip('-')

    @staticmethod
    def camel_to_snake(text: str) -> str:
        """驼峰命名转蛇形命名

        Args:
            text: 驼峰命名字符串

        Returns:
            蛇形命名字符串
        """
        if not text:
            return ""

        # 在大小写转换处插入下划线
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()

    @staticmethod
    def snake_to_camel(text: str, capitalize_first: bool = False) -> str:
        """蛇形命名转驼峰命名

        Args:
            text: 蛇形命名字符串
            capitalize_first: 是否首字母大写

        Returns:
            驼峰命名字符串
        """
        if not text:
            return ""

        components = text.split('_')
        if capitalize_first:
            return ''.join(word.capitalize() for word in components)
        else:
            return components[0] + ''.join(word.capitalize() for word in components[1:])

    @staticmethod
    def reverse(text: str) -> str:
        """反转文本

        Args:
            text: 输入文本

        Returns:
            反转后的文本
        """
        return text[::-1] if text else ""

    @staticmethod
    def shuffle(text: str) -> str:
        """随机打乱文本（简单版本）

        Args:
            text: 输入文本

        Returns:
            打乱后的文本
        """
        import random
        if not text:
            return ""
        chars = list(text)
        random.shuffle(chars)
        return ''.join(chars)

    @staticmethod
    def leetspeak_encode(text: str) -> str:
        """Leetspeak编码（简单版本）

        Args:
            text: 输入文本

        Returns:
            编码后的文本
        """
        if not text:
            return ""

        leet_map = {
            'a': '4', 'e': '3', 'i': '1', 'o': '0', 'u': 'u',
            'A': '4', 'E': '3', 'I': '1', 'O': '0'
        }
        return ''.join(leet_map.get(c, c) for c in text)

    @staticmethod
    def leetspeak_decode(text: str) -> str:
        """Leetspeak解码（简单版本）

        Args:
            text: 输入文本

        Returns:
            解码后的文本
        """
        if not text:
            return ""

        # 简单逆向映射（可能不完整）
        reverse_map = {
            '4': 'a', '3': 'e', '1': 'i', '0': 'o',
            '4': 'A', '3': 'E', '1': 'I', '0': 'O'
        }
        return ''.join(reverse_map.get(c, c) for c in text)

    @staticmethod
    def count_substring(text: str, substring: str) -> int:
        """统计子串出现次数

        Args:
            text: 文本
            substring: 子串

        Returns:
            出现次数
        """
        if not text or not substring:
            return 0
        return text.count(substring)

    @staticmethod
    def find_all(text: str, pattern: str) -> List[tuple]:
        """查找所有匹配项

        Args:
            text: 输入文本
            pattern: 正则表达式模式

        Returns:
            匹配项列表（包含位置信息）
        """
        if not text:
            return []

        matches = []
        for match in re.finditer(pattern, text):
            matches.append((match.group(), match.start(), match.end()))
        return matches

    @staticmethod
    def highlight(text: str, pattern: str, highlight_char: str = '*') -> str:
        """高亮匹配内容

        Args:
            text: 输入文本
            pattern: 正则表达式模式
            highlight_char: 高亮字符

        Returns:
            高亮后的文本
        """
        if not text or not pattern:
            return text or ""

        def replacer(match):
            matched = match.group()
            return highlight_char * len(matched)

        return re.sub(pattern, replacer, text)

    @staticmethod
    def remove_html_tags(text: str) -> str:
        """去除HTML标签

        Args:
            text: 包含HTML的文本

        Returns:
            去除HTML标签后的文本
        """
        if not text:
            return ""

        # 简单HTML标签去除
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    @staticmethod
    def extract_text_between(text: str, start_pattern: str, end_pattern: str) -> List[str]:
        """提取两个模式之间的文本

        Args:
            text: 输入文本
            start_pattern: 起始模式
            end_pattern: 结束模式

        Returns:
            提取的文本列表
        """
        if not text or not start_pattern or not end_pattern:
            return []

        pattern = f'{start_pattern}(.*?){end_pattern}'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches

    @staticmethod
    def count_words(text: str) -> Dict[str, int]:
        """统计词频

        Args:
            text: 输入文本

        Returns:
            词频统计字典
        """
        if not text:
            return {}

        # 提取单词
        words = re.findall(r'\b\w+\b', text.lower())

        # 统计词频
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        return word_count

    @staticmethod
    def get_text_statistics(text: str) -> Dict[str, Any]:
        """获取文本统计信息

        Args:
            text: 输入文本

        Returns:
            统计信息字典
        """
        if not text:
            return {
                'char_count': 0,
                'char_count_no_spaces': 0,
                'word_count': 0,
                'line_count': 0,
                'paragraph_count': 0,
                'sentence_count': 0,
                'avg_word_length': 0,
                'avg_sentence_length': 0
            }

        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        word_count = TextUtils.word_count(text)
        line_count = TextUtils.line_count(text)
        paragraph_count = TextUtils.paragraph_count(text)
        sentence_count = len(TextUtils.split_sentences(text))

        avg_word_length = (char_count_no_spaces / word_count) if word_count > 0 else 0
        avg_sentence_length = (word_count / sentence_count) if sentence_count > 0 else 0

        return {
            'char_count': char_count,
            'char_count_no_spaces': char_count_no_spaces,
            'word_count': word_count,
            'line_count': line_count,
            'paragraph_count': paragraph_count,
            'sentence_count': sentence_count,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2)
        }


# 便捷函数
def clean_text(text: str) -> str:
    """便捷函数：清洗文本"""
    return TextUtils.normalize_unicode(
        TextUtils.collapse_whitespace(
            TextUtils.strip(text)
        )
    )


def extract_keywords(text: str, top_n: int = 10) -> List[tuple]:
    """便捷函数：提取关键词"""
    word_count = TextUtils.count_words(text)
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]


# 使用示例
if __name__ == "__main__":
    # 基础文本转换
    text = "  Hello, World!  "
    print(f"原文本: '{text}'")
    print(f"小写: '{TextUtils.to_lowercase(text)}'")
    print(f"去除空白: '{TextUtils.remove_whitespace(text)}'")
    print(f"折叠空白: '{TextUtils.collapse_whitespace(text)}'")

    # 文本提取
    tweet = "Visit https://example.com #python #coding @john_doe"
    print(f"\nURLs: {TextUtils.extract_urls(tweet)}")
    print(f"Hashtags: {TextUtils.extract_hashtags(tweet)}")
    print(f"Mentions: {TextUtils.extract_mentions(tweet)}")

    # 命名转换
    camel = "myVariableName"
    snake = "my_variable_name"
    print(f"\n驼峰转蛇形: '{TextUtils.camel_to_snake(camel)}'")
    print(f"蛇形转驼峰: '{TextUtils.snake_to_camel(snake)}'")

    # 文本统计
    sample_text = "This is a sample text. It has multiple sentences. Let's count them!"
    stats = TextUtils.get_text_statistics(sample_text)
    print(f"\n文本统计:")
    print(json.dumps(stats, indent=2, default=str))
