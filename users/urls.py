from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.UserList.as_view(), name='user-list'),
    url(r"^add", views.UserCreate.as_view(), name='user-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.UserDetail.as_view(), name='user-detail'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.UserDelete.as_view(), name='user-delete')

]
