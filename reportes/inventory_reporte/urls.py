from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.InventoryList.as_view(), name='inventory-report'),
    url(r"^filter-inventory/$", views.InventoryReportView.as_view(), name="filter-inventory"),
    url(r"^filter-inventory-choices/(?P<field>\w+)$", views.FilterInventoryChoicesView.as_view(), name="get_inventory_choices"),
    url(r"^inventory_generate_report/$", views.DownloadInventoryReportView.as_view(), name="inventory_generate_report"),
    url(r"^inventory_pdf_generate_report/$", views.DownloadInventoryPdfView.as_view(), name="inventory_pdf_generate_report"),
    url(r"^inventory_log_list/$", views.InventoryLogList.as_view(), name="inventory_log_list"),
    url(r"^filter-inventory-log/$", views.InventoryLogsFilterView.as_view(), name="filter-inventory-log"),
    url(r"^generate_inv_log_report/$", views.DownloadInvLogReportView.as_view(), name="generate_inv_log_report"),
    url(r"^generate_inv_log_pdf/$", views.DownloadInvLogPdfView.as_view(), name="generate_inv_log_pdf"),
    url(r"^resultado-de-romaneo/$", views.ResultRomaneoList.as_view(), name='resultado-de-romaneo'),
    url(r"^resultado-de-romaneo-report/$", views.ResultRomaneoFilter.as_view(), name='resultado-de-romaneo-report'),
    ]
