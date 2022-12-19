from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.WarehouseOcupancy.as_view(), name='ocupancy-report'),
    url(r"^filter-ocupancy/$", views.WarehouseOcupancyReportView.as_view(), name="filter-ocupancy"),
    url(r"^filter-ocupancy-choices/(?P<field>\w+)$", views.FilterWarehouseOcupancyChoicesView.as_view(), name="get_ocupancy_choices"),
    url(r"^ocupancy_generate_report/$", views.DownloadWarehouseOcupancyView.as_view(), name="ocupancy_generate_report"),
    url(r"^generate_ocupancy_pdf_report/$", views.DownloadWarehouseOcupancyPdfView.as_view(), name="generate_ocupancy_pdf_report"),
    ]
