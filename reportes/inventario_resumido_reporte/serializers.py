from rest_framework import serializers
from warehouses.warehouse_exit.models import WarehouseExit 
from warehouses.warehouse_entrance.models import WarehouseEntrance


class WarehouseExitSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseEntrance
		fields = '__all__'
