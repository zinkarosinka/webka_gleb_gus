from django import template

register = template.Library()

@register.filter
def split_lines(value):
    return value.split('\n')

@register.filter
def trim(value):
    return value.strip()

@register.filter
def split(value, delimiter):
    return value.split(delimiter)

@register.filter(name='mul')
def mul(value, arg):
    return value * arg

