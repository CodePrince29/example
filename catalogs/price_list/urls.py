from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.PriceListList.as_view(), name='pricelist-list'),
    url(r"^add", views.PriceListCreate.as_view(), name='pricelist-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.PriceListDetail.as_view(), name='pricelist-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.PriceListDelete.as_view(), name='pricelist-delete'),

    url(r"^pricelist_service/$", views.ServiceRelationList.as_view(), name='pricelistservicerelation-list'),
    url(r"^pricelist_service/add", views.ServiceRelationCreate.as_view(), name='pricelistservicerelation-create'),
    url(r"^pricelist_service/(?P<pk>[0-9]+)/$", views.ServiceRelationDetail.as_view(), name='pricelistservicerelation-detail'),
    url(r'^pricelist_service/(?P<pk>[0-9]+)/delete/$', views.ServiceRelationDelete.as_view(), name='pricelistservicerelation-delete'),

]
