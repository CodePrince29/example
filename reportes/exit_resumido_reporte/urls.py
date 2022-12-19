from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.ExitResumidoList.as_view(), name='exit-resumido-report'),
    url(r"^filter-exit-resumido/$", views.ExitResumidoReportView.as_view(), name="filter-exit-resumido"),
    url(r"^filter-resumido-choices/(?P<field>\w+)$", views.FilterExitResumidoChoicesView.as_view(), name="get_exit_resumido_choices"),
    url(r"^generate_resumido_report/$", views.DownloadExitResumidoReportView.as_view(), name="generate_resumido_exit_report"),
    url(r"^generate_resumido_pdf/$", views.DownloadExitResumidoPdfView.as_view(), name="generate_resumido_exit_pdf"),
    ]