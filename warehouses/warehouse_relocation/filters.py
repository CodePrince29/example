import django_filters
from django import forms
from warehouses.warehouse_entrance.models import WarehouseEntrance, WProductMeasurement
from django.db.models import Q
from catalogs.clients.models import Client
from .models import WarehouseRelocation
from catalogs.warehouse.models import Warehouse,WarehouseLocation

def WarehouseEntranceFilter(data):
	werehouse_entrance = [] if data.get('werehouse_entrance') == '' else [data.get('werehouse_entrance')]
	palet_lot =  data.get('palet_lot')
	if len(werehouse_entrance) > 0 and palet_lot != '':		
		queryset_result = WarehouseEntrance.objects.finished_objects().filter(Q(id__in=werehouse_entrance) & Q(warehouseentranceconfirmation__warehouseentrancepallet__palet_lot=palet_lot))
	elif len(werehouse_entrance) == 0 and palet_lot != '':
		queryset_result = WarehouseEntrance.objects.finished_objects().filter(Q(warehouseentranceconfirmation__warehouseentrancepallet__palet_lot=palet_lot))
	elif len(werehouse_entrance) > 0 and palet_lot == '':
		queryset_result = WarehouseEntrance.objects.finished_objects().filter(Q(id__in=werehouse_entrance))
	else:
		queryset_result = None
	return queryset_result


def WarehouseRelocationFilterSet(data, queryset):
	product = [] if data.get('product') == u'' else [data.get('product')]
	if data.get('customer') == 'ALL':
		customer = tuple(Client.objects.all().values_list('id', flat=True))
	else:
		customer = [] if data.get('customer') == u'' else [data.get('customer')]

	if data.get('source_warehouse') == 'ALL':
		source_warehouse = tuple(Warehouse.objects.all().values_list('id', flat=True))
	else:		
		source_warehouse = [] if data.get('source_warehouse') == u'' else [data.get('source_warehouse')]
	
	if data.get('destination_warehouse') == 'ALL':
		destination_warehouse = tuple(Warehouse.objects.all().values_list('id', flat=True))
	else:		
		destination_warehouse = [] if data.get('destination_warehouse') == u'' else [data.get('destination_warehouse')]
	
	source_location = [] if data.get('source_location') == u'' else [data.get('source_location')]
	destination_location = [] if data.get('destination_location') == u'' else [data.get('destination_location')]
	filterdata = filter_data(customer, product, source_warehouse, source_location, destination_warehouse, destination_location, data.get('start_date'), data.get('end_date'))
	
	queryset_result = queryset.filter(filterdata)
	return queryset_result

def filter_data(customer, product, source_warehouse, source_location, destination_warehouse,
	destination_location, start, end):
	if len(customer) > 0 and (start and end != None) and len(product) > 0 and len(source_warehouse) > 0 and len(source_location) > 0 and len(destination_warehouse) > 0 and len(destination_location) > 0:
		
		return (Q(customer_id__in=customer)&
				Q(created_at__lte=end)&
				Q(created_at__gte= start) & 
				Q(product_id__in=product)&
				Q(source_warehouse__in=source_warehouse)&
				Q(source_location__in=source_location)&
				Q(destination_warehouse_id__in=destination_warehouse)&
				Q(destination_location_id__in=destination_warehouse))

	elif len(customer) == 0 and (start and end != None) and len(source_warehouse) > 0 and len(source_location) > 0 and len(destination_warehouse) > 0 and len(destination_location) > 0:
		return (Q(created_at__lte=end)&
				Q(created_at__gte= start) & 
				Q(source_warehouse__in=source_warehouse)&
				Q(source_location__in=source_location)&
				Q(destination_warehouse_id__in=destination_warehouse)&
				Q(destination_location_id__in=destination_warehouse))

	elif len(customer) > 0 and (start and end == None) and len(product) > 0 and len(source_warehouse) > 0 and len(source_location) > 0 and len(destination_warehouse) > 0 and len(destination_location) > 0:
		return (Q(customer_id__in=customer)&
				Q(product_id__in=product)&
				Q(source_warehouse__in=source_warehouse)&
				Q(source_location__in=source_location)&
				Q(destination_warehouse_id__in=destination_warehouse)&
				Q(destination_location_id__in=destination_warehouse))


	elif len(customer) > 0 and (start and end != None) and len(product) > 0 and len(source_warehouse) == 0  and len(destination_warehouse) > 0 and len(destination_location) > 0:
		return (Q(customer_id__in=customer)&
				Q(created_at__lte=end)&
				Q(created_at__gte= start) & 
				Q(product_id__in=product)&
				Q(destination_warehouse_id__in=destination_warehouse)&
				Q(destination_location_id__in=destination_warehouse))


	elif len(customer) > 0 and (start and end != None) and len(product) > 0 and len(source_warehouse) > 0 and len(source_location) > 0 and len(destination_warehouse) == 0:
		
		return (Q(customer_id__in=customer)&
				Q(created_at__lte=end)&
				Q(created_at__gte= start) & 
				Q(product_id__in=product)&
				Q(source_warehouse__in=source_warehouse)&
				Q(source_location__in=source_location))

	else:
		return (Q(customer_id__in=customer) |
				Q(created_at__lte=end) |
				Q(created_at__gte= start)  | 
				Q(product_id__in=product) |
				Q(source_warehouse__in=source_warehouse) |
				Q(source_location__in=source_location) |
				Q(destination_warehouse_id__in=destination_warehouse) |
				Q(destination_location_id__in=destination_warehouse))