from rest_framework import serializers
from ..models import Notification
from warehouses.warehouse_entrance.models import WarehouseEntrance
from warehouses.warehouse_exit.models import WarehouseExit
from warehouses.warehouse_exit.serializers import WarehouseEntranceNotificationSerializer, WarehouseExitNotificationSerializer


class ContentObjectRelatedField(serializers.RelatedField):
    """
    Custom field for content object related field representation.
    Returns the correct serializer class depending on the content object.
    """

    def to_representation(self, value):
        if isinstance(value, WarehouseEntrance):
            serializer = WarehouseEntranceNotificationSerializer(value)
        elif isinstance(value, WarehouseExit):
            serializer = WarehouseExitNotificationSerializer(value)
        else:
            raise Exception('Unexpected type of related object')

        return serializer.data


class NotificationSerializer(serializers.ModelSerializer):
    content_object = ContentObjectRelatedField(read_only=True, many=False)
    
    class Meta:
        model = Notification
        fields = (
            'id','content_object', 'occurred_dt', 'object_class_name', 'content_type','message','status','deleted_by'
        )
