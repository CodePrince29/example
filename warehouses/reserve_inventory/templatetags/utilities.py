from django import template
from django.utils.safestring import mark_safe
from catalogs.clients.models import Client
from catalogs.product.models import Product
register = template.Library()

@register.assignment_tag
def get_client():
	return Client.objects.all()

@register.assignment_tag	
def get_product():
	return Product.objects.all()