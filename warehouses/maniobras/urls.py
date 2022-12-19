from django.conf.urls import url
from .views import get_pallet_peso_variable, save_inventory_romaneo_peso_variables, PalletConsultView,pallet_information_list,WarehousePaletListQrcode,PalletReprintView,EntrancesList,InventoryTakingView,ReportInventoryTakingView,UpdateInventoryTakingView,ShowInventoryTakingView,CreateInventoryTakingView, ExitList, EntrancesUpdateView, NewEntrancesUpdateView, ConfirmEntrancePallet,ExitUpdateView, ConfirmExitPallet,update_pallet_note,DownloadComparisonPdfView, MeoverasEntrancesList, MeoverasExitList, NewExitUpdateView, NewPallletConsilated, get_inventory_detail, save_consolidate

urlpatterns = [
    url(r"^entrances-list$", EntrancesList.as_view(), name='maniobras-entrance-list'),
    url(r"^exit-list$", ExitList.as_view(), name='maniobras-exit-list'),
    url(r"^confirm-entrance_pallet/(?P<pk>[0-9]+)$", ConfirmEntrancePallet.as_view(), name="confirm-entrance_pallet"),
    url(r"^confirm-exit_pallet/(?P<pk>[0-9]+)$", ConfirmExitPallet.as_view(), name="confirm-exit_pallet"),
    url(r"^entrance-update/(?P<pk>[0-9]+)$", EntrancesUpdateView.as_view(), name='maniobras-entrance-update'),
    url(r"^exit-update/(?P<pk>[0-9]+)$", ExitUpdateView.as_view(), name='maniobras-exit-update'),
    url(r"^inventory_taking$", InventoryTakingView.as_view(), name='inventory-taking-list'),
    url(r"^add-inventory-taking$", CreateInventoryTakingView.as_view(), name='inventory-taking-create'),
    url(r"^update-inventory-taking/(?P<pk>[0-9]+)$", UpdateInventoryTakingView.as_view(), name='inventory-taking-update'),
    url(r"^show-inventory-taking/(?P<pk>[0-9]+)$", ShowInventoryTakingView.as_view(), name='inventory-taking-show'),
    url(r"^report-inventory-taking/(?P<pk>[0-9]+)/$", ReportInventoryTakingView.as_view(), name='inventory-taking-report'),
    url(r"^pallet-consult$", PalletConsultView.as_view(), name='pallet-consult-list'),
    url(r"^pallet-reprint$", PalletReprintView.as_view(), name='pallet-reprint'),
    url(r"^pallet_information_list$", pallet_information_list, name='pallet-information-list'),
    url(r"^pallet-qr-print$", WarehousePaletListQrcode.as_view(), name='pallet-qr-print'),
    url(r'^update-pallet-note$', update_pallet_note, name="update-pallet-note"),
    url(r'^generate_inventory_comparison_report$', DownloadComparisonPdfView.as_view(), name="generate-inventory-comparison-report"),
    
    url(r"^get-inventory-peso-variable/(?P<pk>[0-9]+)$", get_pallet_peso_variable, name='get-inventory-peso-variable'),
    url(r"^save-inventory-peso-variable/(?P<pk>[0-9]+)$", save_inventory_romaneo_peso_variables, name='save-inventory-peso-variable'),
    url(r"^maniobras-entrances-list$", MeoverasEntrancesList.as_view(), name='maniobras-list'),
    url(r"^maniobras-entrance-edit/(?P<pk>[0-9]+)$", NewEntrancesUpdateView.as_view(), name='entrance-edit'),
    url(r"^maniobras-exit-list$", MeoverasExitList.as_view(), name='maniobras-exit-list'),
    url(r"^maniobras-exit-edit/(?P<pk>[0-9]+)$", NewExitUpdateView.as_view(), name='maniobras-exit-edit'),
    url(r"^pallet-consolidate", NewPallletConsilated.as_view(), name='pallet-consolidate'),
    url(r"^get-inventory-detail", get_inventory_detail, name='get-inventory-detail'),
    url(r"^save-consolidate", save_consolidate, name='save-consolidate'),



]