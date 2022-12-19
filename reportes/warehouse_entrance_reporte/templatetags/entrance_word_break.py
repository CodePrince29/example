from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def entrance_word_break(word):
	import textwrap
	return "Hiiii"



