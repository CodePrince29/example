# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from auditlog.registry import auditlog
from .models import *

# Register your models here.
admin.site.register(TakingInventory)
auditlog.register(TakingInventory)
