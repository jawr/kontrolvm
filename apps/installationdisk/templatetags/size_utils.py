from django import template
register = template.Library()

@register.filter(name='to_human_readable')
def to_human_readable(value):
  if value < 1024:
    return '%d B' % (value)
  elif value < (1024 * 1024):
    return '%.2f KB' % (value/1024.0)
  elif value < (1024 * 1024 * 1024):
    return '%.2f MB' % (value/1024/1024.0)
  elif value < (1024 * 1024 * 1024 * 1024):
    return '%.2f GB' % (value/1024/1024/1024.0)
  else:
    return '%.2f TB' % (value/1024/1024/1024/1024.0)
