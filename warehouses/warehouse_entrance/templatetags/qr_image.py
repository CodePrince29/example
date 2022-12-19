from django import template

from django.contrib.sites.models import Site

register = template.Library()


@register.inclusion_tag('pdf/qr_tag.html', takes_context=True)
def qr_image(context, text="No Data", width=100, height=100):
    return {'text': text,'width': width, 'height': height}