from django.urls import reverse
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def profile_link(user, request_user, capitalize=True):
	if user.id == request_user.id:
		if capitalize:
			return mark_safe('You')
		else:
			return mark_safe('you')
	else:
		url = reverse('user_profile', args=[user.username])
		return mark_safe('<a href="%s">%s</a>' % (url, user.username))
