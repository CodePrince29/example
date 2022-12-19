from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.EntrancesResumidoList.as_view(), name='entrances-resumido-report'),
    url(r"^filter-entrance-resumido/$", views.EntranceResumidoReportView.as_view(), name="filter-entrance-resumido"),
    url(r"^filter-resumido-choices/(?P<field>\w+)$", views.FilterResumidoChoicesView.as_view(), name="get_resumido_choices"),
    url(r"^generate_resumido_report/$", views.DownloadEntranceResumidoReportView.as_view(), name="generate_resumido_report"),
    url(r"^generate_resumido_pdf/$", views.DownloadEntranceResumidoPdfView.as_view(), name="generate_resumido_pdf"),
    ]