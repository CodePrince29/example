from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ClientList.as_view(), name='client-list'),
    url(r"^add", views.ClientCreate.as_view(), name='client-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.ClientDetail.as_view(), name='client-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.ClientDelete.as_view(), name='client-delete'),
    url(r"^change_customer_password$", views.change_password, name='change-customer-password'),
]
