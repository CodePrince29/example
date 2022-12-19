from django import template
import pdb
from django.contrib.sites.models import Site

register = template.Library()

@register.filter(name='debugger')
def debugger(obj):
	pdb.set_trace()