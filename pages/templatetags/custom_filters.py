# pages/templatetags/custom_filters.py
from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def add_days(date_str, days):
    """将日期字符串加上指定天数"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        new_date = date_obj + timedelta(days=int(days))
        return new_date.strftime("%Y-%m-%d")
    except:
        return date_str

@register.filter
def multiply(value, arg):
    """将值乘以参数"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def divide(value, arg):
    """将值除以参数"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return ''