from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.ExitList.as_view(), name='exit-report'),
    url(r"^filter-exit/$", views.ExitReportView.as_view(), name="filter-exit"),
    url(r"^filter-exit-choices/(?P<field>\w+)$", views.FilterExitChoicesView.as_view(), name="get_exit_choices"),
    url(r"^exit_generate_report/$", views.DownloadExitReportView.as_view(), name="exit_generate_report"),
    url(r"^generate_exit_pdf_report/$", views.DownloadExitPdfView.as_view(), name="generate_exit_pdf_report"),
    ]