from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ServiceList.as_view(), name='service-list'),
    url(r"^add", views.ServiceCreate.as_view(), name='service-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.ServiceDetail.as_view(), name='service-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.ServiceDelete.as_view(), name='service-delete'),

]