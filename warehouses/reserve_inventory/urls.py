from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.InventoryReservedList.as_view(), name='inventory-reserve-list'),
    url(r"^add", views.InventoryReservedCreate.as_view(), name='inventory-reserve-create'),
    url(r"^(?P<pk>[0-9]+)/$", views.InventoryReservedUpdate.as_view(), name='inventory-reserve-update'),
    url(r"^inventory_filter_list$", views.filter_inventory, name='inventory-filter-list'),
    url(r"^release_reserved_inventory$", views.release_reserved_inventory, name='release-reserved-inventory'),
    
    ]

