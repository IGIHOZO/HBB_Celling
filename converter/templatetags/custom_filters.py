from django import template

register = template.Library()

@register.filter
def intcomma(value):
    """
    Convert an integer to a string containing commas every three digits.
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value
    
    if value < 0:
        return '-' + intcomma(-value)
    
    s = str(value)
    if len(s) <= 3:
        return s
    
    groups = []
    while s:
        groups.append(s[-3:])
        s = s[:-3]
    
    return ','.join(reversed(groups))

@register.filter
def split(value, separator=','):
    """
    Split a string into a list using the specified separator.
    """
    if not value:
        return []
    return str(value).split(separator)

@register.filter  
def strip(value):
    """
    Strip whitespace from a string.
    """
    if not value:
        return ''
    return str(value).strip()

@register.filter
def add(value, arg=1):
    """
    Add a number to a value.
    """
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value
