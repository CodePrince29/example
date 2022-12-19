from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ProductFamilyList.as_view(), name='productfamily-list'),
    url(r"^add", views.ProductFamilyCreate.as_view(), name='productfamily-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.ProductFamilyDetail.as_view(), name='productfamily-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.ProductFamilyDelete.as_view(), name='productfamily-delete'),

]