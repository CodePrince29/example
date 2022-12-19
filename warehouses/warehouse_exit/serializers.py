from rest_framework import serializers
from warehouses.warehouse_entrance.models import WarehouseEntrance, WarehouseEntranceConfirmation
from catalogs.warehouse.models import WarehouseLocation, Warehouse


class WarehouseEntranceFilterSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseEntrance
  		fields = '__all__'

class WarehouseEntranceNotificationSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseEntrance
  		fields = ('id','status','absolute_url','absolute_maneobras_url')

class WarehouseExitNotificationSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseEntrance
  		fields = ('id','status','absolute_url','absolute_maneobras_url')

class WarehouseEntranceConfirmationSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseEntranceConfirmation
		fields = '__all__'


class WarehouseSerializer(serializers.ModelSerializer):
	class Meta:
		model = Warehouse
		fields = ('id', 'code',)
