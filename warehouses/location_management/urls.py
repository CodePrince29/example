from django.conf.urls import url
from .views import WarehouseLocationsAPIView
from . import views
urlpatterns = [
    url(r"^$", views.WarehouseLocationsAPIView.as_view(), name='location-management-search'),
   	url(r'^warehouse-location-manage/(?P<pk>[0-9]+)/$', views.warehouse_location_block_unblock, name="warehouse-location-blocked"),
]