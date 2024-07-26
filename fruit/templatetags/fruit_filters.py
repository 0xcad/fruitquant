from django import template
import os

from datetime import datetime

register = template.Library()

@register.filter
def remove_na(value):
    if not value:
        return False
    return [x for x in value if x != "N/A"]

@register.filter
def comma_separated(value):
    if len(value) > 1:
        value = remove_na(value)
    return ", ".join(value)

"""@register.filter
def get_date(value):
    date_str = list(value)[0]
    date = datetime.strptime(date_str, '%m/%d/%Y')
    return datetime.strftime(date, '%Y-%m-%d')

def minmax(value, fn):
    arr = [float(x) for x in value if x and x.replace('.', '', 1).isdigit()]
    if not arr:
        return "N/A"
    return fn(arr)


@register.filter
def max_filter(value):
    return minmax(value, max)

@register.filter
def min_filter(value):
    return minmax(value, min)"""
