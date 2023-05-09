from django import template
from django.utils.safestring import mark_safe
from anviserver.secrets import ANALYTICS_SCRIPT_BLOCK

register = template.Library()

@register.simple_tag
def analytics_script_block():
    return mark_safe(ANALYTICS_SCRIPT_BLOCK)
