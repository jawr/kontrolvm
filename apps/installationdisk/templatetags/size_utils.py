from django import template
register = template.Library()

@register.filter(name='to_human_readable')
def to_human_readable(value):
  if value < 1024:
    return '%d Bytes' % (value)
  elif value < (1024 * 1024):
    return '%.2f KBytes' % (value/1024.0)
  elif value < (1024 * 1024 * 1024):
    return '%.2f MBytes' % (value/1024/1024.0)
  elif value < (1024 * 1024 * 1024 * 1024):
    return '%.2f GBytes' % (value/1024/1024/1024.0)
  else:
    return '%.2f TBytes' % (value/1024/1024/1024/1024.0)
