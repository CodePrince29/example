from django.contrib import admin
from auditlog.registry import auditlog
from .models import Product

# Register your models here.
auditlog.register(Product)
