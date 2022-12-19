from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.HistoryList.as_view(), name='warehouse-history-list'),
    url(r"^warehouse-history/$", views.WarehouseEntranceProductFilter.as_view(), name='warehouse-entrance-list'),
]
