from django import template
from django.utils.safestring import mark_safe
from catalogs.clients.models import Client
from catalogs.product.models import Product

register = template.Library()

@register.simple_tag
def word_break(word):
	import textwrap
	return textwrap.fill(word,10)



