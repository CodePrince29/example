from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.PackagingList.as_view(), name='packaging-list'),
    url(r"^add", views.PackagingCreate.as_view(), name='packaging-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.PackagingDetail.as_view(), name='packaging-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.PackagingDelete.as_view(), name='packaging-delete'),

]