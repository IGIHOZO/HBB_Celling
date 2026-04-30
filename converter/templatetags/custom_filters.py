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
