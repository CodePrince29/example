from django.conf.urls import url
from .api.controller import ListTimeSlotsView, ListBranchesView
from . import views

urlpatterns = [
    url(r"^warehouse/$", views.WarehouseList.as_view(), name='warehouse-list'),
    url(r"^bays$", ListTimeSlotsView.as_view(), name='warehouse-bays'),
    url(r"^branch/list$", views.WarehouseBranchList.as_view(), name='branch-list'),
    url(r"^branch/create$", views.WarehouseBranchCreate.as_view(), name='branch-create'),
    url(r"^branch/(?P<pk>[0-9]+)/delete$", views.WarehouseBranchDelete.as_view(), name='branch-delete'),
    url(r"^branch/(?P<pk>[0-9]+)/update$", views.WarehouseBranchUpdate.as_view(), name='branch-update'),

    url(r"^branches$", ListBranchesView.as_view(), name='warehouse-branches'),
    url(r"^warehouse/add", views.WarehouseCreate.as_view(), name='warehouse-create'),
    url(r"^warehouse/(?P<pk>[0-9]+)/$", views.WarehouseDetail.as_view(), name='warehouse-detail'),
    url(r'^warehouse/(?P<pk>[0-9]+)/delete/$', views.WarehouseDelete.as_view(), name='warehouse-delete'),
    url(r'^warehouse_inventories$', views.WarehouseInventoryList.as_view(), name='warehouse-inventory-list'),
    url(r'^inventory-filter$', views.WarehouseInventoryFilterAPI.as_view(), name='warehouse-inventory-filter-api'),
    url(r"^warehouse_inventories/(?P<pk>[0-9]+)/edit$", views.WarehouseInventoryEdit.as_view(), name='warehouse-inventory-edit'),
    # url(r"^warehouse-location/$", views.WarehouseLocationList.as_view(), name='warehouselocation-list'),
    # url(r"^warehouse-location/add", views.WarehouseLocationCreate.as_view(), name='warehouselocation-create'),
    url(r"^warehouse-location/(?P<pk>[0-9]+)/$", views.WarehouseLocationDetail.as_view(),
        name='warehouselocation-detail'),
    url(r'^warehouseproduct-filter/(?P<pk>[0-9]+)/$', views.WarehouseProductFilter.as_view(),
        name='warehouseproduct-filter'),
    url(r'^warehouselocation-product/(?P<warehouse>[0-9]+)/(?P<location>[0-9]+)/(?P<customer>[0-9]+)$', views.WarehouseLocationProduct.as_view(),
        name='warehouselocation-product'),

    url(r"^warehouse/(?P<pk>[0-9]+)/update_details$", views.WarehouseUpdateDetails.as_view(), name='warehouse-update-details'),
    url(r"^update_depth_warehouse/$", views.WarehouseUpdateDepthAPI.as_view(), name='warehouse-depth-update'),

    url(r"^warehouse/(?P<pk>[0-9]+)/qr_code_generater$", views.WarehouseQRCodeGenerater.as_view(), name='warehouse-qr-code-generater'),
    url(r"^warehouse/qr_code_printer$", views.WarehouseQRCodePrinter.as_view(), name='warehouse-qr-code-printer'),
    
    url(r"^warehouse/assign_short_code$", views.warehouse_assign_short_code, name='warehouse-assign_short_code'),
    url(r"^warehouse/get-warehouse-location-detail$", views.get_warehouse_location_detail, name='get-warehouse-location-detail'),


]
