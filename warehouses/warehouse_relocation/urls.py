from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^$", views.RelocationList.as_view(), name='relocation-list'),
    url(r"^add", views.RelocationCreate.as_view(), name='relocation-create'),
    url(r"^relocation-api/$", views.WarehouseRelocationAPI.as_view(), name='warehouse-relocation-api'),
    url(r'^warehouse/(?P<pk>[\w]+)/locations$', views.WarehouseLocationAPI.as_view(), name='warehouse-locations'),
    url(r'^relocation-filter$', views.WarehouseRelocationFilterAPI.as_view(), name='warehouse-relocation-filter-api'),
    url(r'^(?P<pk>[0-9]+)/detail$', views.RelocationShowView.as_view(), name="relocation-detail"),
    url(r'^entrance-confirmation-product/(?P<entrance>[0-9]+)/(?P<product>[0-9]+)/(?P<customer>[0-9]+)$', views.WarehouseConfirmationProduct.as_view(),
        name='entrance-confirmation-product'),

    url(r'^relocation-destination-weight-volume/$', views.RelocationWeightVolume.as_view(),name='warehouselocation-weight-volume'),
    url(r'^relocation-shortcode-weight-volume/$', views.RelocationWeightVolumeShortCode.as_view(),name='relocation-shortcode-weight-volume'),
    url(r'^save-relocation-from-shortcode/$', views.SaveRelocationFromShortCode.as_view(),name='save-relocation-from-shortcode'),

    url(r'^relocation-exit-shortcode-weight-volume/$', views.RelocationExitWeightVolumeShortCode.as_view(),name='relocation-exit-shortcode-weight-volume'),
    url(r'^save-exit-relocation-from-shortcode/$', views.SaveExitRelocationFromShortCode.as_view(),name='save-exit-relocation-from-shortcode'),


]