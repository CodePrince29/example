from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ..models import Notification
from .serializers import NotificationSerializer
from warehouses.warehouse_entrance.models import WarehouseEntrance
from warehouses.warehouse_exit.models import WarehouseExit
from rest_framework.views import APIView
from rest_framework.response import Response
import json


class NotificationsList(generics.ListAPIView):
	serializer_class = NotificationSerializer
	permission_classes = (IsAuthenticated,)
	

	def get_queryset(self):
		"""
		This view should return a list of all the notifications of the
		currently logged in user.
		"""
		user = self.request.user

		if user.role and user.role.name == 'Sistemas':
			
			return Notification.objects.filter(status=False).exclude(deleted_by__contains=[user.pk])

		elif user.role and user.role.name == 'Jefe Almacen':
			entrance_pending_notifies = list(WarehouseEntrance.objects.filter(status='pending', notifications__isnull=False).values_list('notifications', flat=True))
			entrance_maneuver_complete_notifies = list(WarehouseEntrance.objects.filter(status='ManeuverComplete', notifications__isnull=False).values_list('notifications', flat=True))
			exit_pending_notifies = list(WarehouseExit.objects.filter(status='pending', notifications__isnull=False).values_list('notifications', flat=True))
			exit_maneuver_complete_notifies = list(WarehouseExit.objects.filter(status='ManeuverComplete', notifications__isnull=False).values_list('notifications', flat=True))
			filter_data = list(set(entrance_pending_notifies + entrance_maneuver_complete_notifies + exit_pending_notifies + exit_maneuver_complete_notifies))
			
			return Notification.objects.filter(pk__in = filter_data,status=False).exclude(deleted_by__contains=[user.pk])

		elif user.role and user.role.name == 'Jefe Administracion':
			entrance_notifies = list(WarehouseEntrance.objects.filter(status='pending', notifications__isnull=False).values_list('notifications', flat=True))
			exit_notifies = list(WarehouseExit.objects.filter(status='pending', notifications__isnull=False).values_list('notifications', flat=True))
			return Notification.objects.filter(pk__in=list(set(entrance_notifies+exit_notifies)),status=False).exclude(deleted_by__contains=[user.pk])

		elif user.role and user.role.name == 'Almacen Maniobras':
			entrance_in_maneuvers_notifies = list(WarehouseEntrance.objects.filter(status='InManeuvers', notifications__isnull=False).values_list('notifications', flat=True))
			exit_in_maneuvers_notifies = list(WarehouseExit.objects.filter(status='InManeuvers', notifications__isnull=False).values_list('notifications', flat=True))
			data = list(set(entrance_in_maneuvers_notifies + exit_in_maneuvers_notifies))
			return Notification.objects.filter(pk__in=data,status=False).exclude(deleted_by__contains=[user.pk])

		elif user.role and user.role.name == 'Responsable de Turno Almacen':
			entrance_maneuver_complete_notifies = list(WarehouseEntrance.objects.filter(status='ManeuverComplete', notifications__isnull=False).values_list('notifications', flat=True))
			exit_maneuver_complete_notifies = list(WarehouseExit.objects.filter(status='ManeuverComplete', notifications__isnull=False).values_list('notifications', flat=True))
			data = list(set(entrance_maneuver_complete_notifies + exit_maneuver_complete_notifies))
			return Notification.objects.filter(pk__in=data,status=False).exclude(deleted_by__contains=[user.pk])

		else:
			return Notification.objects.none()

class UpdateNotificationStatus(APIView):
	def put(self, request, pk, format=None):
		notification = Notification.objects.get(pk=pk)
		serializer = NotificationSerializer(notification, data=request.data,partial=True)
		if serializer.is_valid():
			if serializer.save():
				return Response({'data':serializer.data,'code':200})
		return Response({'data':serializer.errors,'code':500})

class DeleteNotification(APIView):
	def post(self, request):
		
		notification_ids = request.POST.getlist('notification_ids[]')
		notifications = Notification.objects.filter(pk__in=notification_ids)
		if notifications.exists():
			notifications.update(deleted_by=[self.request.user.id])
			return Response({'code':200})
		return Response({'code':500})

