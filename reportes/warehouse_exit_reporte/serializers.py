from warehouses.warehouse_exit.models import WarehouseExit
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
class WarehouseExitSerializer(serializers.ModelSerializer):
	customer = serializers.SerializerMethodField('get_customer_name')
	status = serializers.SerializerMethodField('get_status_name')
	class Meta:
		model = WarehouseExit
		fields = ( 'id','exit_date', 'exit_hour', 'customer', 'status',)

	def get_customer_name(self, obj):
		return obj.customer.name

	def get_status_name(self, obj):
		if obj.status == 'finish':
			return """<spna class="label label-primary">{0}</spna>""".format(_('Finish'))
		else:
			return """<spna class="label label-default">{0}</spna>""".format(_('Pending'))