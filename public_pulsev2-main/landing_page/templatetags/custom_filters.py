from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter and return list"""
    if value:
        # Handle both string and list inputs
        if isinstance(value, str):
            return [item.strip() for item in value.split(delimiter) if item.strip()]
        elif isinstance(value, list):
            return value
    return []

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def to_list(value):
    """Convert string to list if needed"""
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        return [item.strip() for item in value.split(',') if item.strip()]
    return []

@register.filter
def join_list(value, delimiter=', '):
    """Join list into string"""
    if isinstance(value, list):
        return delimiter.join([str(item) for item in value])
    return str(value)