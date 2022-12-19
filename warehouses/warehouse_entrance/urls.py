from django.conf.urls import url
from .api.views import save_romaneo_weights, check_peso_variable_quantity, save_romaneo_peso_variables, update_romaneo_product_total_kg, CustomerProductsAPIView,get_location,get_pallet_detail, get_pallets_list, WarehouseLocationsConfirmationAPIView,WarehouseAvailabilityApiView,get_rack_location, BoxesAvailabilityApiView,get_pallet_peso_variable,save_entrance_pallet, entrance_pallet_details, save_pallet_measurement, get_single_pallet_detail, save_pallet_location, get_pallet_from_entrance, get_prev_next_pallet, get_pallet_detail_for_relocation, compare_measurement_pallet
from . import views
from .controller import NewEntranceView, UpdateEntranceView, WarehouseEntranceList, ConfirmEntrancePalletView, EntranceList, EditEntranceView, ConfirmSingleEntrancePalletView, NewConfirmEntrancePalletView, EntranceNewView, NewEntranceConfirmation
from django.views.decorators.cache import cache_page, never_cache

ctime = (60 * 2) # 2 min
urlpatterns = [
    url(r"^(?P<pk>[0-9]+)/detail/$", views.EntranceDetail.as_view(), name='entrance-detail'),
    url(r'^(?P<pk>[0-9]+)/entrance-delete/$', views.NewEntranceDelete.as_view(), name='new-entrance-delete'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.EntranceDelete.as_view(), name='entrance-delete'),
    url(r'^customer-products/(?P<pk>[\w]+)/$', CustomerProductsAPIView.as_view({'get': 'list'}), name="customer-products"),
    url(r'^warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$', WarehouseLocationsConfirmationAPIView.as_view({'get': 'list'}), name="warehouseentrance-confirmation"),
    url(r'^(?P<pk>[0-9]+)/download-entrace-invoice/$', views.DownloadEntranceInvoiceUpdate.as_view(), name="download-invoice"),
    url(r'^check-warehouse-availability$', WarehouseAvailabilityApiView.as_view(),
        name='check-warehouse-availability'),
    url(r'^get-rack/(?P<warehouse>[0-9]+)/$', get_rack_location, name="get-rack"),
    url(r'^get-location/$', get_location, name="get-location"),
    url(r'^check-boxes-availability$', BoxesAvailabilityApiView.as_view(),
        name='check-boxes-availability'),

    url(r'^get-entrance-palet-qrcode$', views.GetWarehousePaletQrcode.as_view(),
        name='get-entrance-palet-qrcode'),
    url(r'^get-pallet-detail/(?P<pallet>[0-9]+)/$', get_pallet_detail, name="get-pallet-detail"),
    url(r'^get-pallets-list/(?P<customer>[0-9]+)/(?P<product>[0-9-A-z]+)$', get_pallets_list, name="get_pallets_list"),
    

    url(r'^get-pallet-peso-variable/(?P<pallet>[0-9]+)/$', get_pallet_peso_variable, name="get-pallet-peso-variable"),
    url(r'^save-romaneo-weights$', save_romaneo_weights, name="save_romaneo_weights"),
    # url(r'^save-romaneo-product-weight$', save_romaneo_product_weight, name="save-romaneo-product-weight"),
    url(r'^save-entrance-pallet$', save_entrance_pallet, name="save-entrance-pallet"),

    url(r'^new-entrance$',  NewEntranceView.as_view(), name="new-entrance"),
    url(r'^update-entrance/(?P<pk>[0-9]+)$', cache_page(ctime)(UpdateEntranceView.as_view()), name="update-entrance"),
    url(r"^warehouse-entrances-list$",  WarehouseEntranceList.as_view(), name='warehouse-entrances-list'),
    url(r'^confirm-entrance-pallets/(?P<pk>[0-9]+)$', never_cache(ConfirmEntrancePalletView.as_view()), name="confirm-entrance-pallets"),
    url(r'^update-romaneo-product-total_kg$', update_romaneo_product_total_kg, name="update_romaneo_product_total_kg"),
    url(r'^save-romaneo-peso-variables/(?P<pk>[0-9]+)$', save_romaneo_peso_variables, name="save_romaneo_peso_variables"),
    url(r'^check-peso-variables-quantity$', check_peso_variable_quantity, name="check_peso_variable_quantity"),
    url(r"^entrances-list$",  EntranceList.as_view(), name='entrances-list'),
    url(r'^edit-entrance/(?P<pk>[0-9]+)$', EditEntranceView.as_view(), name="edit-entrance"),
    url(r'^entrance-pallet-details/(?P<pk>[0-9]+)$', ConfirmSingleEntrancePalletView.as_view() , name="entrance_pallet_details"),
    url(r'^new-confirm-entrance-pallets/(?P<pk>[0-9]+)$', never_cache(NewConfirmEntrancePalletView.as_view()), name="new-confirm-entrance-pallets"),
    url(r'^entrance-new$',  EntranceNewView.as_view(), name="entrance-new"),
    url(r'^save-pallet-measurement$', save_pallet_measurement, name="save-pallet-measurement"),
    url(r'^get-single-pallet-detail$', get_single_pallet_detail, name="get-single-pallet-detail"),
    url(r'^save-pallet-location$', save_pallet_location, name="save-pallet-location"),
    url(r'^get-pallet-from-entrance$', get_pallet_from_entrance, name="get-pallet-from-entrance"),
    url(r'^get-prev-next-pallet$', get_prev_next_pallet, name="get-prev-next-pallet"),
    url(r'^entrance-pallet-detail-for-relocation$', get_pallet_detail_for_relocation, name="entrance-pallet-detail-for-relocation"),
    url(r'^new-entrance-confirmation/(?P<pk>[0-9]+)$', NewEntranceConfirmation.as_view(), name="new-entrance-confirmation"),
    url(r'^compare-box-total-kg/(?P<pk>[0-9]+)$', compare_measurement_pallet, name="compare-box-total-kg"),
    url(r'^(?P<pk>[0-9]+)/entrance-resultado-romaneo/$', views.EntranceResultadoRomaneo.as_view(), name="entrance-resultado-romaneo"),

]

