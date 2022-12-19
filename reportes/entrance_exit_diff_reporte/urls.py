from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.EntrancesList.as_view(), name='entrance-exit-diff-report'),
    url(r"^filter-entrance-exit-diff/$", views.EntranceReportView.as_view(), name="filter-entrance-exit-diff"),
    url(r"^filter-entrance-exit-diff/(?P<field>\w+)$", views.FilterChoicesView.as_view(), name="get-entrance-exit-diff-choices"),
    url(r"^generate-entrance-exit-diff/$", views.DownloadEntranceReportView.as_view(), name="generate-entrance-exit-pdf-report"),
    url(r"^generate-entrance-exit-diff-report/$", views.DownloadEntrancePdfView.as_view(), name="generate-entrance-exit-csv-diff-report"),
    ]