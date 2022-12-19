from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.VehicleList.as_view(), name='vehicle-list'),
    url(r"^add", views.VehicleCreate.as_view(), name='vehicle-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.VehicleParamUpdate.as_view(), name='vehicle-update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.VehicleDelete.as_view(), name='vehicle-delete'),

]