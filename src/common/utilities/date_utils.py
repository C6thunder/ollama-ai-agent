"""日期时间工具模块

提供各种日期时间处理功能
包括格式转换、日期计算、时间戳处理等
"""

import datetime
from typing import Union, Dict, List, Optional
import calendar


class DateUtils:
    """日期时间工具类"""

    @staticmethod
    def now(tz: Optional[str] = None) -> datetime.datetime:
        """获取当前时间

        Args:
            tz: 时区名称（如 'Asia/Shanghai'），None 表示本地时间

        Returns:
            当前时间
        """
        if tz:
            from zoneinfo import ZoneInfo
            return datetime.datetime.now(ZoneInfo(tz))
        return datetime.datetime.now()

    @staticmethod
    def today() -> datetime.date:
        """获取今天的日期"""
        return datetime.date.today()

    @staticmethod
    def yesterday() -> datetime.date:
        """获取昨天的日期"""
        return DateUtils.today() - datetime.timedelta(days=1)

    @staticmethod
    def tomorrow() -> datetime.date:
        """获取明天的日期"""
        return DateUtils.today() + datetime.timedelta(days=1)

    @staticmethod
    def parse_date(date_str: str) -> datetime.datetime:
        """解析日期字符串

        Args:
            date_str: 日期字符串（支持多种格式）

        Returns:
            解析后的日期时间对象
        """
        # 尝试多种日期格式
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d",
            "%Y/%m/%d %H:%M:%S",
            "%m/%d/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M:%S"
        ]

        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"无法解析日期字符串: {date_str}")

    @staticmethod
    def format_date(
        date: Union[datetime.datetime, datetime.date],
        format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """格式化日期

        Args:
            date: 日期对象
            format_str: 格式字符串

        Returns:
            格式化后的日期字符串
        """
        if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            date = datetime.datetime.combine(date, datetime.time())
        return date.strftime(format_str)

    @staticmethod
    def to_timestamp(date: Union[datetime.datetime, datetime.date]) -> int:
        """转换为时间戳

        Args:
            date: 日期对象

        Returns:
            Unix时间戳（秒）
        """
        if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            date = datetime.datetime.combine(date, datetime.time())
        return int(date.timestamp())

    @staticmethod
    def from_timestamp(timestamp: int) -> datetime.datetime:
        """从时间戳创建日期

        Args:
            timestamp: Unix时间戳（秒）

        Returns:
            日期时间对象
        """
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def add_days(date: Union[datetime.datetime, datetime.date], days: int) -> datetime.date:
        """日期加天数

        Args:
            date: 起始日期
            days: 要增加的天数

        Returns:
            结果日期
        """
        if isinstance(date, datetime.datetime):
            date = date.date()
        return date + datetime.timedelta(days=days)

    @staticmethod
    def subtract_days(date: Union[datetime.datetime, datetime.date], days: int) -> datetime.date:
        """日期减天数

        Args:
            date: 起始日期
            days: 要减少的天数

        Returns:
            结果日期
        """
        return DateUtils.add_days(date, -days)

    @staticmethod
    def add_hours(date: datetime.datetime, hours: int) -> datetime.datetime:
        """日期加小时

        Args:
            date: 起始时间
            hours: 要增加的小时数

        Returns:
            结果时间
        """
        return date + datetime.timedelta(hours=hours)

    @staticmethod
    def subtract_hours(date: datetime.datetime, hours: int) -> datetime.datetime:
        """日期减小时

        Args:
            date: 起始时间
            hours: 要减少的小时数

        Returns:
            结果时间
        """
        return DateUtils.add_hours(date, -hours)

    @staticmethod
    def add_minutes(date: datetime.datetime, minutes: int) -> datetime.datetime:
        """日期加分钟

        Args:
            date: 起始时间
            minutes: 要增加的分钟数

        Returns:
            结果时间
        """
        return date + datetime.timedelta(minutes=minutes)

    @staticmethod
    def subtract_minutes(date: datetime.datetime, minutes: int) -> datetime.datetime:
        """日期减分钟

        Args:
            date: 起始时间
            minutes: 要减少的分钟数

        Returns:
            结果时间
        """
        return DateUtils.add_minutes(date, -minutes)

    @staticmethod
    def difference_days(start_date: datetime.date, end_date: datetime.date) -> int:
        """计算两个日期相差的天数

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            相差的天数
        """
        return (end_date - start_date).days

    @staticmethod
    def difference_hours(start_time: datetime.datetime, end_time: datetime.datetime) -> float:
        """计算两个时间相差的小时数

        Args:
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            相差的小时数
        """
        return (end_time - start_time).total_seconds() / 3600

    @staticmethod
    def difference_minutes(start_time: datetime.datetime, end_time: datetime.datetime) -> float:
        """计算两个时间相差的分钟数

        Args:
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            相差的分钟数
        """
        return (end_time - start_time).total_seconds() / 60

    @staticmethod
    def is_weekend(date: datetime.date) -> bool:
        """判断是否为周末

        Args:
            date: 日期

        Returns:
            是否为周末
        """
        return date.weekday() >= 5

    @staticmethod
    def is_weekday(date: datetime.date) -> bool:
        """判断是否为工作日

        Args:
            date: 日期

        Returns:
            是否为工作日
        """
        return date.weekday() < 5

    @staticmethod
    def get_week_number(date: datetime.date) -> int:
        """获取一年中的第几周

        Args:
            date: 日期

        Returns:
            周数
        """
        return date.isocalendar()[1]

    @staticmethod
    def get_day_of_week(date: datetime.date) -> str:
        """获取星期几

        Args:
            date: 日期

        Returns:
            星期几（中文）
        """
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[date.weekday()]

    @staticmethod
    def get_month_name(date: datetime.date) -> str:
        """获取月份名称

        Args:
            date: 日期

        Returns:
            月份名称（中文）
        """
        months = [
            "", "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"
        ]
        return months[date.month]

    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """获取某月的天数

        Args:
            year: 年份
            month: 月份

        Returns:
            天数
        """
        return calendar.monthrange(year, month)[1]

    @staticmethod
    def get_first_day_of_month(date: datetime.date) -> datetime.date:
        """获取某月的第一天

        Args:
            date: 日期

        Returns:
            月份第一天
        """
        return date.replace(day=1)

    @staticmethod
    def get_last_day_of_month(date: datetime.date) -> datetime.date:
        """获取某月的最后一天

        Args:
            date: 日期

        Returns:
            月份最后一天
        """
        year, month = date.year, date.month
        last_day = calendar.monthrange(year, month)[1]
        return date.replace(day=last_day)

    @staticmethod
    def get_first_day_of_year(date: datetime.date) -> datetime.date:
        """获取某一年的第一天

        Args:
            date: 日期

        Returns:
            年份第一天
        """
        return date.replace(month=1, day=1)

    @staticmethod
    def get_last_day_of_year(date: datetime.date) -> datetime.date:
        """获取某一年的最后一天

        Args:
            date: 日期

        Returns:
            年份最后一天
        """
        return date.replace(month=12, day=31)

    @staticmethod
    def start_of_week(date: datetime.date) -> datetime.date:
        """获取一周的开始（星期一）

        Args:
            date: 日期

        Returns:
            周一日期
        """
        return date - datetime.timedelta(days=date.weekday())

    @staticmethod
    def end_of_week(date: datetime.date) -> datetime.date:
        """获取一周的结束（星期日）

        Args:
            date: 日期

        Returns:
            周日日期
        """
        return date + datetime.timedelta(days=6 - date.weekday())

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """判断是否为闰年

        Args:
            year: 年份

        Returns:
            是否为闰年
        """
        return calendar.isleap(year)

    @staticmethod
    def get_age(birth_date: datetime.date) -> int:
        """计算年龄

        Args:
            birth_date: 出生日期

        Returns:
            年龄
        """
        today = DateUtils.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    @staticmethod
    def business_days_between(
        start_date: datetime.date,
        end_date: datetime.date,
        include_start: bool = True,
        include_end: bool = True
    ) -> int:
        """计算两个日期之间的业务天数（排除周末）

        Args:
            start_date: 开始日期
            end_date: 结束日期
            include_start: 是否包含开始日期
            include_end: 是否包含结束日期

        Returns:
            业务天数
        """
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        business_days = 0
        current_date = start_date

        while current_date <= end_date:
            # 调整起始日期
            if current_date == start_date and not include_start:
                current_date += datetime.timedelta(days=1)
                continue

            # 调整结束日期
            if current_date == end_date and not include_end:
                break

            if DateUtils.is_weekday(current_date):
                business_days += 1

            current_date += datetime.timedelta(days=1)

        return business_days

    @staticmethod
    def get_holidays(year: int) -> List[datetime.date]:
        """获取指定年份的节假日列表（简化版，仅包含固定节假日）

        Args:
            year: 年份

        Returns:
            节假日列表
        """
        holidays = [
            datetime.date(year, 1, 1),   # 元旦
            datetime.date(year, 5, 1),   # 劳动节
            datetime.date(year, 10, 1),  # 国庆节
        ]

        # 添加农历节日（简化，实际应该使用农历转换库）
        # 这里仅作为示例

        return holidays

    @staticmethod
    def is_holiday(date: datetime.date) -> bool:
        """判断是否为节假日

        Args:
            date: 日期

        Returns:
            是否为节假日
        """
        holidays = DateUtils.get_holidays(date.year)
        return date in holidays

    @staticmethod
    def to_iso_format(date: Union[datetime.datetime, datetime.date]) -> str:
        """转换为ISO格式

        Args:
            date: 日期对象

        Returns:
            ISO格式字符串
        """
        if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            date = datetime.datetime.combine(date, datetime.time())
        return date.isoformat()

    @staticmethod
    def get_timezone_info(tz: Optional[str] = None) -> Dict[str, str]:
        """获取时区信息

        Args:
            tz: 时区名称

        Returns:
            时区信息字典
        """
        if tz:
            from zoneinfo import ZoneInfo
            now = datetime.datetime.now(ZoneInfo(tz))
        else:
            now = datetime.datetime.now()

        return {
            "timezone": str(now.tzinfo) if now.tzinfo else "本地时间",
            "offset": now.strftime("%z"),
            "dst": now.dst() is not None
        }

    @staticmethod
    def convert_timezone(
        dt: datetime.datetime,
        target_tz: str,
        source_tz: Optional[str] = None
    ) -> datetime.datetime:
        """转换时区

        Args:
            dt: 要转换的时间
            target_tz: 目标时区
            source_tz: 源时区，None 表示本地时间

        Returns:
            转换后的时间
        """
        from zoneinfo import ZoneInfo

        if source_tz:
            dt = dt.replace(tzinfo=ZoneInfo(source_tz))
        return dt.astimezone(ZoneInfo(target_tz))


# 便捷函数
def get_current_time(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前时间字符串

    Args:
        format_str: 格式字符串

    Returns:
        格式化后的时间字符串
    """
    return DateUtils.format_date(DateUtils.now(), format_str)


def get_current_date(format_str: str = "%Y-%m-%d") -> str:
    """获取当前日期字符串

    Args:
        format_str: 格式字符串

    Returns:
        格式化后的日期字符串
    """
    return DateUtils.format_date(DateUtils.today(), format_str)


# 使用示例
if __name__ == "__main__":
    # 获取当前时间
    now = DateUtils.now()
    print(f"当前时间: {DateUtils.format_date(now)}")

    # 日期运算
    today = DateUtils.today()
    print(f"明天: {DateUtils.format_date(DateUtils.tomorrow())}")
    print(f"昨天: {DateUtils.format_date(DateUtils.yesterday())}")

    # 日期差计算
    start = datetime.date(2024, 1, 1)
    end = datetime.date(2024, 12, 31)
    print(f"2024年总天数: {DateUtils.difference_days(start, end) + 1}")
    print(f"2024年业务天数: {DateUtils.business_days_between(start, end)}")

    # 格式转换
    timestamp = DateUtils.to_timestamp(now)
    print(f"时间戳: {timestamp}")
    print(f"从时间戳恢复: {DateUtils.format_date(DateUtils.from_timestamp(timestamp))}")

    # 日期信息
    print(f"今天星期几: {DateUtils.get_day_of_week(today)}")
    print(f"当前月份: {DateUtils.get_month_name(today)}")
    print(f"本月天数: {DateUtils.get_days_in_month(today.year, today.month)}")
    print(f"是否为闰年: {DateUtils.is_leap_year(today.year)}")
