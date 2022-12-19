from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.CarrierList.as_view(), name='carrier-list'),
    url(r"^add", views.CarrierCreate.as_view(), name='carrier-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.CarrierParamUpdate.as_view(), name='carrier-update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.CarrierDelete.as_view(), name='carrier-delete'),

]