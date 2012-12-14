from django import template
register = template.Library()

@register.filter(name='message_level_as_text')
def message_level_as_text(value):
  if value == 125 or value == 25:
    return 'success'
  elif value == 120 or value == 20:
    return 'info'
  elif value == 130 or value == 30:
    return 'warning'
  elif value == 140 or value == 40:
    return 'error'
