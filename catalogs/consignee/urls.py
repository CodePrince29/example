from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ConsigneeList.as_view(), name='consignee-list'),
    url(r"^add", views.ConsigneeCreate.as_view(), name='consignee-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.ConsigneeParamUpdate.as_view(), name='consignee-update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.ConsigneeDelete.as_view(), name='consignee-delete'),

]