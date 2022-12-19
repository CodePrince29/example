from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ProductList.as_view(), name='product-list'),
    url(r"^add", views.ProductCreate.as_view(), name='product-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.ProductDetail.as_view(), name='product-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.ProductDelete.as_view(), name='product-delete'),
    url(r'^product-update/$',views.location_update ,name='product-update')

]
