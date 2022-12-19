from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.Trazabilidad.as_view(), name='trazabilidad-reporte'),
    url(r"^filter-trazabilidad/$", views.TrazabilidadReportView.as_view(), name="filter-trazabilidad"),
    url(r'^trazabilidad-generate-report/(?P<pallet>[0-9]+)/$', views.DownloadTrazabilidadView.as_view(), name="trazabilidad-generate-report"),
    # url(r"^trazabilidad_generate_report/$", views.DownloadTrazabilidadView.as_view(), name="trazabilidad_generate_report"),
    #url(r"^generate_trazabilidad_pdf_report/$", views.DownloadTrazabilidadPdfView.as_view(), name="generate_trazabilidad_pdf_report"),
    ]
