from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sga.settings')
app = Celery('sga')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

from celery.decorators import task
from celery.utils.log import get_task_logger
import requests
 
@task
def updateCache(rurl):
	response = requests.get(settings.BASE_URL+rurl)
	print(response)

@task
def delete_bays(types, id):
	from warehouses.warehouse_entrance.models import WarehouseEntrance
	if types == "entrance":
		obj = WarehouseEntrance.objects.get(id=id)
		obj.bays.all().delete()
	else:
		from warehouses.warehouse_exit.models import WarehouseExit
		obj = WarehouseExit.objects.get(id=id)
		obj.bays.all().delete()