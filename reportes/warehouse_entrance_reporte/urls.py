from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.EntrancesList.as_view(), name='entrances-report'),
    url(r"^filter-entrance/$", views.EntranceReportView.as_view(), name="filter-entrance"),
    url(r"^filter-choices/(?P<field>\w+)$", views.FilterChoicesView.as_view(), name="get_field_choices"),
    url(r"^generate_report/$", views.DownloadEntranceReportView.as_view(), name="generate_report"),
    url(r"^generate_pdf_report/$", views.DownloadEntrancePdfView.as_view(), name="generate_pdf_report"),
    ]