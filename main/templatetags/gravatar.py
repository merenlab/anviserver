import hashlib
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def gravatar(email, size=40):
    return mark_safe("https://www.gravatar.com/avatar/" + hashlib.md5(email.lower().encode('utf-8')).hexdigest() + "?s=" + str(size))
