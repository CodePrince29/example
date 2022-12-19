from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import WarehouseTruckBays, Branch

from catalogs.general_params.models import GeneralParams
import pdb
from django.utils import timezone
from datetime import datetime
from rest_framework import serializers
from django.utils.timezone import localtime, make_aware

class TimeSlotsSerializer(serializers.ModelSerializer):
	time = serializers.SerializerMethodField()
	date = serializers.SerializerMethodField()
	class Meta:
		model = WarehouseTruckBays		
		fields = ( 'bay','loading', 'time','date',)

	def get_time(self, obj):
		return localtime(obj.time_slot).strftime("%I:%M %p")

	def get_date(self, obj):
		return obj.time_slot.strftime("%Y-%M-%d")

class ListBranchesView(APIView):
	def get(self, request):
		branchs = Branch.objects.values('id', 'name')
		return Response({'branches': branchs})

class ListTimeSlotsView(APIView):
	def get(self, request):
		WarehouseTruckBays.objects.filter(time_slot__date__lt=timezone.now().date(), branch_id=request.GET.get('branch')).update(loading=False)
		bays = WarehouseTruckBays.objects.filter(time_slot__date=request.GET.get('date'), loading=True, branch_id=request.GET.get('branch'))
		branch = Branch.objects.get(id=request.GET.get('branch'))
		
		time_duration = branch.service_interval*60
		todays_bay = bays.filter(time_slot__date=timezone.now().date())
		for bay in todays_bay:
			if (bay.time_slot + timezone.timedelta(minutes=time_duration)) < timezone.now():
				bay.loading = False
				bay.save()
		today = make_aware(datetime.strptime('01-01-2000 05:00 AM', '%d-%m-%Y %H:%M %p'))

		date_list = [today + timezone.timedelta(minutes=time_duration*x) for x in range(0, int(24/branch.service_interval))]
		time_slots = [x.strftime('%H:%M %p') for x in date_list ]
		return Response({'message': 'Time slots fetched successfully', 'data': {'reservations':TimeSlotsSerializer(bays, many=True).data, 'time_slots': time_slots, 'allowed_bays': branch.total_bays}, 'code': 200})

