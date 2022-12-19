from django.conf.urls import url

from .api.views import check_print_picking, update_exit_romaneo_product_kg, WarehouseLocationsAPIView, WarehouseLocationsConfirmationAPIView,get_pallet_peso_variable,save_pallet_peso_variable,save_exit_pallet,save_romaneo_product_weight, get_prev_next_pallet, confirm_exit_pallet
from . import views
from .controller import NewExitView, ConfirmPalletView, WarehouseExitList, UpdateExitView, NewWarehouseExitList, NewWarehouseExitView, NewUpdateExitView, ConfirmWarehouseExitView, exit_print_picking, get_pallet_detail_for_relocation
from django.views.decorators.cache import cache_page, never_cache

ctime = (60 * 2) # 2 min
urlpatterns = [
    # url(r"^$", views.ExitList.as_view(), name='exit-list'),
    # url(r"^add", views.ExitCreate.as_view(), name='exit-create'),
    url(r"^(?P<pk>[0-9]+)/check-print-picking$", check_print_picking, name='check_print_picking'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.ExitDelete.as_view(), name='exit-delete'),
    url(r'^(?P<pk>[0-9]+)/detail/$', views.ExitParamShow.as_view(), name='exit-detail'),
    url(r'^warehouse-location/(?P<pk>[0-9]+)/$', WarehouseLocationsAPIView.as_view({'get': 'list'}), name="warehouse-location"),
    url(r'^warehouse-location-detail/(?P<pk>[0-9]+)/$', views.get_warehouse_locations, name="warehouse-location-detail"),
    url(r'^warehouse-exit-location-detail/$', views.get_warehouse_exit_locations, name="warehouse-exit-location-detail"),
    url(r'^warehouse-location-manage/(?P<pk>[0-9]+)/$', views.get_location_for_manage, name="warehouse-location-manage"),
    url(r'^warehouse-exit-confirmation/(?P<pk>[0-9]+)/$', WarehouseLocationsConfirmationAPIView.as_view({'get': 'list'}), name="warehouseexit-confirmation"),
    url(r'^(?P<pk>[0-9]+)/download-exit-invoice/$', views.DownloadExitInvoiceUpdate.as_view(), name="download-invoice"),
    url(r'^exit_filter_for_location/$', views.WarehouseFilterAPI.as_view(), name="exit-filter-warehouse-location"),
    url(r'^print-picking/(?P<pk>[0-9]+)/$', views.PrintPickingView.as_view(), name="print-picking"),
    url(r'^auto-picking$', views.AutoPickingView.as_view(), name="auto-picking"),
    url(r'^get-pallet-peso-variable/(?P<pallet>[0-9]+)/$', get_pallet_peso_variable, name="exit-get-pallet-peso-variable"),
    url(r'^save-pallet-peso-variable$', save_pallet_peso_variable, name="exit-save-pallet-peso-variable"),
    url(r'^exit-save-romaneo-product-weight$', save_romaneo_product_weight, name="exit-save-romaneo-product-weight"),
    url(r'^exit-update-romaneo-product-kg$', update_exit_romaneo_product_kg, name="update_exit_romaneo_product_kg"),
    

    url(r'^clear-sessions$', views.ClearSession.as_view(), name="clear-sessions"),
    url(r'^save-exit-pallet$', save_exit_pallet, name="save-exit-pallet"),

    url(r'^new-exit$', NewExitView.as_view(), name="new-exit"),
    url(r'^update-exit/(?P<pk>[0-9]+)$', cache_page(ctime)(UpdateExitView.as_view()), name="update-exit"),
    url(r"^warehouse-exit-list$", WarehouseExitList.as_view(), name='warehouse-exit-list'),
    url(r'^confirm-exit-pallets/(?P<pk>[0-9]+)$', never_cache(ConfirmPalletView.as_view()), name="confirm-exit-pallets"),
    url(r'^check_retained_quantity$', views.CheckRetainedQuantity.as_view(), name="check_retained_quantity"),
    #new url started for new requirement
    url(r"^new-warehouse-exit-list$", NewWarehouseExitList.as_view(), name='new-warehouse-exit-list'),
    url(r'^new-warehouse-exit$', NewWarehouseExitView.as_view(), name="new-warehouse-exit"),
    url(r'^new-update-exit/(?P<pk>[0-9]+)$', NewUpdateExitView.as_view(), name="new-update-exit"),
    url(r'^auto-print-picking$', views.AutoPrintPickingView.as_view(), name="auto-auto-picking"),
    url(r'^confirm-warehouse-exit/(?P<pk>[0-9]+)$', ConfirmWarehouseExitView.as_view(), name="confirm-warehouse-exit"),
    url(r'^exit-pallet-details/(?P<pk>[0-9]+)$', get_prev_next_pallet , name="exit-pallet-details"),
    url(r'^confirm-exit-pallet/(?P<pk>[0-9]+)$', confirm_exit_pallet , name="confirm-exit-pallet"),
    url(r'^exit-print-picking/(?P<pk>[0-9]+)$', exit_print_picking, name="exit-print-picking"),
    url(r'^exit-pallet-detail-for-relocation$', get_pallet_detail_for_relocation, name="exit-pallet-detail-for-relocation"),
    url(r'^(?P<pk>[0-9]+)/exit-resultado-romaneo/$', views.ExitResultadoRomaneo.as_view(), name="exit-resultado-romaneo"),
    
    ]

