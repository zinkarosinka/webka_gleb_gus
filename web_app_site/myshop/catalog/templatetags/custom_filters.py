# catalog/templatetags/custom_filters.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='split_lines')
def split_lines(value):
    return [line.strip() for line in value.split('\n') if line.strip()]

@register.filter
def split(value, delimiter=None):
    return value.split(delimiter) if delimiter else list(value)

@register.filter
def trim(value):
    return value.strip()

@register.filter(name='mul')
def mul(value, arg):
    return value * arg

