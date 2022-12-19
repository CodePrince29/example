from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.UnitList.as_view(), name='unit-list'),
    url(r"^add", views.UnitCreate.as_view(), name='unit-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.UnitDetail.as_view(), name='unit-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.UnitDelete.as_view(), name='unit-delete'),

]
