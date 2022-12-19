import django_filters
from django import forms
from warehouses.warehouse_entrance.models import WarehouseEntrance, WProductMeasurement
from warehouses.warehouse_exit.models import WarehouseExit
from django.db.models import Q
from catalogs.clients.models import Client
import pdb

def EntranceFilter(data):
	product = [] if data.get('product') == '' else [data.get('product')]
	
	if data.get('client') == 'ALL':
		customer = tuple(Client.objects.all().values_list('id', flat=True))
	else:
		customer = [] if data.get('client') == '' else [data.get('client')]

	queryset_result = WarehouseEntrance.objects.filter(filter_data(customer, data.get('start_date'), data.get('end_date'), product))
	return tuple(queryset_result.distinct('id'))



def ExitFilter(data):
	product = [] if data.get('product') == '' else [data.get('product')]
	if data.get('client') == 'ALL':
		customer = tuple(Client.objects.all().values_list('id', flat=True))
	else:
		customer = [] if data.get('client') == '' else [data.get('client')]

	queryset_result = WarehouseExit.objects.filter(filter_data_exit(customer, data.get('start_date'), data.get('end_date'), product))
	return tuple(queryset_result.distinct('id'))

def filter_data(customer, start, end, product):
	if len(customer) > 0 and (start !='' and end != '') and len(product) > 0:
		return (Q(customer_id__in=customer)& Q(entrance_date__lte=end) 
			& Q(entrance_date__gte= start) & 
			Q(warehouseentranceconfirmation__product_id__in=product)
			& Q(status="finish"))
	
	elif len(customer) > 0 and (start == '' and end == '') and len(product) == 0:
		return (Q(customer_id__in=customer)& Q(status="finish"))

	elif len(customer) > 0 and (start !='' and end != '') and len(product) == 0:
		return (Q(customer_id__in=customer)& Q(entrance_date__lte=end) 
			& Q(entrance_date__gte= start)& Q(status="finish"))

	elif len(customer) == 0 and (start !='' and end != '') and len(product) > 0:
		return (Q(warehouseentranceconfirmation__product_id__in=product)
			& Q(entrance_date__lte=end) 
			& Q(entrance_date__gte= start) & Q(status="finish"))

	elif len(customer) == 0 and (start == '' and end == '') and len(product) > 0:
		return (Q(warehouseentranceconfirmation__product_id__in=product)& Q(status="finish"))

	elif len(customer) == 0 and (start !='' and end != '') and len(product) == 0:
		return (Q(entrance_date__lte=end) & Q(entrance_date__gte= start) & Q(status="finish"))

def filter_data_exit(customer, start, end, product):
	if len(customer) > 0 and (start !='' and end != '') and len(product) > 0:
		return (Q(customer_id__in=customer)& Q(exit_date__lte=end) 
			& Q(exit_date__gte= start) & 
			Q(wexitconfirmation__product_id__in=product)& Q(status="finish"))
	
	elif len(customer) > 0 and (start == '' and end == '') and len(product) == 0:
		return (Q(customer_id__in=customer)& Q(status="finish"))

	elif len(customer) > 0 and (start !='' and end != '') and len(product) == 0:
		return (Q(customer_id__in=customer)& Q(exit_date__lte=end) 
			& Q(exit_date__gte= start)& Q(status="finish"))

	elif len(customer) == 0 and (start !='' and end != '') and len(product) > 0:
		return (Q(wexitconfirmation__product_id__in=product)
			& Q(exit_date__lte=end) 
			& Q(exit_date__gte= start)& Q(status="finish"))

	elif len(customer) == 0 and (start == '' and end == '') and len(product) > 0:
		return (Q(wexitconfirmation__product_id__in=product)& Q(status="finish"))

	elif len(customer) == 0 and (start !='' and end != '') and len(product) == 0:
		return (Q(exit_date__lte=end) & Q(exit_date__gte= start)& Q(status="finish"))