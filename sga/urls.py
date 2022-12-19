"""sga URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from sga import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from catalogs.notifications.api.views import *
from users.views import login_view, logout_view, menuover_login_validation


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', login_required(TemplateView.as_view(template_name='dashboard.html')), name='main-dashboard'),
    url(r'^login/', login_view, name='login'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^advanced_filters/', include('advanced_filters.urls')),
    url(r'^gp/', include('catalogs.general_params.urls')),
    url(r'^packaging/', include('catalogs.packaging.urls')),
    url(r'^product/', include('catalogs.product.urls')),
    url(r'^productfamily/', include('catalogs.product_family.urls')),
    url(r'^unit/', include('catalogs.units.urls')),
    url(r'^service/', include('catalogs.service.urls')),
    url(r'^client/', include('catalogs.clients.urls')),
    url(r'^pricelist/', include('catalogs.price_list.urls')),
    url(r'^warehouses/', include('catalogs.warehouse.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^vehicles/', include('catalogs.vehicle.urls')),
    url(r'^carriers/', include('catalogs.carrier.urls')),
    url(r'^consigees/', include('catalogs.consignee.urls')),
    url(r'^warehouse_entrance/', include('warehouses.warehouse_entrance.urls')),
    url(r'^warehouse_exit/', include('warehouses.warehouse_exit.urls')),
    url(r'^warehouse_history/', include('warehouses.warehouse_history.urls')),
    url(r'^warehouse_relocation/', include('warehouses.warehouse_relocation.urls')),
    url(r'^location_management/', include('warehouses.location_management.urls')),
    url(r'^entrance_reportes/', include('reportes.warehouse_entrance_reporte.urls')),
    url(r'^exit_reportes/', include('reportes.warehouse_exit_reporte.urls')),
    url(r'^inventory_reportes/', include('reportes.inventory_reporte.urls')),
    url(r'^warehouse_ocupancy_reporte/', include('reportes.warehouse_ocupancy_reporte.urls')),
    url(r'^entradas_resumido_reporte/', include('reportes.entradas_resumido_reporte.urls')),
    url(r'^exit_resumido_reporte/', include('reportes.exit_resumido_reporte.urls')),
    url(r'^inventario_resumido_reporte/', include('reportes.inventario_resumido_reporte.urls')),
    url(r'^trazabilidad_reporte/', include('reportes.trazabilidad_reporte.urls')),
    url(r'^maneuver/', include('warehouses.maniobras.urls')),
    url(r'^inventory_reserve/', include('warehouses.reserve_inventory.urls')),
    url(r'^api/notifications/$', NotificationsList.as_view()),
    url(r'^notifications/update-status/(?P<pk>[0-9]+)$', UpdateNotificationStatus.as_view()),
    url(r'^notifications/delete_notifications/$', DeleteNotification.as_view()),
    url(r'^entrance_exit_diff_reportes/', include('reportes.entrance_exit_diff_reporte.urls')),
    
    url(r'^menuover_login_validation/', menuover_login_validation, name='menuover_login_validation'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT);
