from django import template
from django.utils.safestring import mark_safe


register = template.Library()

@register.simple_tag
def text_break(word):
	import textwrap
	return textwrap.fill(word,10)



