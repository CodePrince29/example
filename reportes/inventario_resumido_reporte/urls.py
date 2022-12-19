from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.InventarioResumidoList.as_view(), name='inventario-resumido-report'),
    url(r"^inventario-resumido-filter/$", views.InventryResumidoFilter.as_view(), name='inventario-resumido-filter'),
    url(r"^generate_inventory_resumido_report/$", views.DownloadInventoryResumidoReportView.as_view(), name="generate_inventory_resumido_report"),
    url(r"^inventory_summary_generate_pdf/$", views.DownloadInventorySummeryPdfView.as_view(), name="inventory_summary_generate_pdf"),
    ] 