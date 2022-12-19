from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.CapacityList.as_view(), name='gp-list'),
    url(r"^add", views.GeneralParamCreate.as_view(), name='gp-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.GeneralParamUpdate.as_view(), name='gp-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.GeneralParamDelete.as_view(), name='gp-delete'),

]
