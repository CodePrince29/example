# r'^warehouse/(?P<pk>[0-9]+)/update_details/$',
# r'^update_depth_warehouse/$',

#Customer Login





CUSTOMER_LOGIN_URLS = (
    r'^$',
    r'^/login/$',
    r'^warehouse_entrance/$',
    r'^warehouse_entrance/add$',
    r'^warehouse_exit/$',
    r'^warehouse_exit/add$',
    #new changes
    r'^warehouse_entrance/warehouse-entrances-list$',
    r'^warehouse_entrance/new-entrance$',   
    r'^warehouse_exit/warehouse-exit-list$',
    r'^warehouse_exit/new-exit$',

    r'^warehouse_entrance/customer-products/(?P<pk>[\w]+)/$',
    r'^warehouse_history/$',
    r'^warehouse_history/warehouse-history/$',
    r'^client/change_customer_password',
    r'^warehouse_entrance/(?P<pk>[0-9]+)/detail/$',
    r'^warehouse_entrance/(?P<pk>[0-9]+)/download-entrace-invoice/$',
    r'^warehouse_exit/(?P<pk>[0-9]+)/detail/$',
    r'^warehouse_exit/(?P<pk>[0-9]+)/download-exit-invoice/$',
    r'^warehouses/branches$',
    r'^warehouses/bays$',

    # ------- New process started -----------
   #------new maniobras process started ---------
   r'^maneuver/get-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/save-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-entrances-list$',
   r'^maneuver/maniobras-entrance-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-exit-list$',
   r'^maneuver/maniobras-exit-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consolidate$',
   r'^maneuver/get-inventory-detail$',
   r'^maneuver/save-consolidate$',
   r'^warehouse_relocation/relocation-shortcode-weight-volume/$',
   r'^warehouse_relocation/save-relocation-from-shortcode/$',
   r'^warehouses/warehouse/get-warehouse-location-detail$',
   r'^warehouse_relocation/relocation-exit-shortcode-weight-volume/$',   
   r'^warehouse_relocation/save-exit-relocation-from-shortcode/',
   #------new maniobras process ended -----------

   # ------- New Exit process started -----------
   r'^warehouse_exit/$',
   r'^warehouse_exit/new-warehouse-exit-list$',
   r'^warehouse_exit/new-warehouse-exit$',
   r'^warehouse_exit/new-update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/auto-print-picking$',
   r'^warehouse_exit/confirm-warehouse-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/confirm-exit-pallet/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-print-picking/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-detail-for-relocation$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/exit-resultado-romaneo/$',
   # ------- New Exit process ended -----------------

   # ------- New Entrance process started -----------
   r'^warehouse_entrance/entrance-new$',
   r'^warehouse_entrance/entrances-list$',
   r'^warehouse_entrance/edit-entrance/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/entrance-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/new-confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/save-pallet-measurement$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   r'^warehouse_entrance/get-single-pallet-detail$',
   r'^warehouse_entrance/save-pallet-location$',
   r'^warehouse_entrance/get-pallet-from-entrance$',
   r'^warehouse_entrance/get-prev-next-pallet$',
   r'^warehouse_entrance/entrance-pallet-detail-for-relocation$',
   r'^warehouse_entrance/new-entrance-confirmation/(?P<pk>[0-9]+)$',   
   r'^warehouse_entrance/compare-box-total-kg/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/entrance-resultado-romaneo/$',
   r'^inventory_reportes/resultado-de-romaneo/',
   r'^inventory_reportes/resultado-de-romaneo-report/',
   r'^inventory_reserve/$',
   r'^inventory_reserve/add$',
   r'^inventory_reserve/(?P<pk>[0-9]+)/$',
   r'^inventory_reserve/inventory_filter_list$',
   r'^inventory_reserve/release_reserved_inventory$',
   # ------- New Entrance process ended ----------

   # ------- New Requirement Details -------------
    )


#Direccion Login Url
DIRECCION_LOGIN_URLS = (
   r'^$',
   r'^/login/$',
   #client
   r'^client/$',
   r'^client/add$',
   r'^client/(?P<pk>[0-9]+)/$',
   r'^client/(?P<pk>[0-9]+)/delete/$',
   #product
   r'^product/$',
   r'^product/add$',
   r'^product/(?P<pk>[0-9]+)/$',
   r'^product/(?P<pk>[0-9]+)/delete/$',
   r'^product-update/$',

   #warehouse-inventory
   r'^warehouses/warehouse_inventories$',
   r'^warehouses/inventory-filter$',
   r'^warehouses/warehouse_inventories/(?P<pk>[0-9]+)/edit$',
   #warehouse_entrance
   r'^warehouse_entrance/$',
   r'^warehouse_entrance/add$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_entrance/customer-products/(?P<pk>[\w]+)/$',
   r'^warehouse_entrance/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/download-entrace-invoice/$',
   r'^warehouse_entrance/get-rack/(?P<warehouse>[0-9]+)/$',
   r'^warehouse_entrance/get-location/$',

   r'^warehouse_entrance/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_entrance/save-pallet-peso-variable$',
   r'^warehouse_entrance/save-entrance-pallet$',
   r'^warehouse_entrance/get-entrance-palet-qrcode$',
   r'^warehouse_entrance/save-romaneo-product-weight$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/check-print-picking$',
   r'^warehouse_entrance/save-romaneo-peso-variables/(?P<pk>[0-9]+)$',
   #new changes
   r'^warehouse_entrance/warehouse-entrances-list$',
   r'^warehouse_entrance/new-entrance$',
   r'^warehouse_entrance/confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/update-entrance/(?P<pk>[0-9]+)$',


    #warehouse_exit
   r'^warehouse_exit/$',
   r'^warehouse_exit/add$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_exit/warehouse-location/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-location-detail/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-location-detail/$',
   r'^warehouse_exit/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/download-exit-invoice/$',
   r'^warehouse_exit/exit_filter_for_location/$',
   r'^warehouse_exit/print-picking/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/auto-picking$',
   r'^warehouse_exit/save-exit-pallet$',

   r'^warehouse_exit/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_exit/save-pallet-peso-variable$',
   r'^warehouse_exit/exit-save-romaneo-product-weight$',

   #new changes
   r'^warehouse_exit/warehouse-exit-list$',
   r'^warehouse_exit/new-exit$',
   r'^warehouse_exit/confirm-exit-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/clear-sessions$',

   #location_management
   r'^location_management/$',
   r'^location_management/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   #warehouse_history
   r'^warehouse_history/$',
   r'^warehouse_history/warehouse-history/$',
    #warehouse_relocation
   r'^warehouse_relocation/$',
   r'^warehouse_relocation/add$',
   r'^warehouse_relocation/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_relocation/relocation-api/$',   
   r'^warehouse_relocation/warehouse/(?P<pk>[\w]+)/locations$',
   r'^warehouse_relocation/relocation-filter$',
   r'^warehouse_relocation/entrance-confirmation-product/(?P<entrance>[0-9]+)/(?P<product>[0-9]+)/(?P<customer>[0-9]+)$',
   r'^warehouse_relocation/relocation-destination-weight-volume/$',

   #entrance_reportes
   r'^entrance_reportes/$',
   r'^entrance_reportes/filter-entrance/$',
   r'^entrance_reportes/generate_report/$',
   r'^entrance_reportes/generate_pdf_report/$',
   r'^entrance_reportes/filter-choices/(?P<field>\w+)$',
   r'^trazabilidad_reporte/$',
   r'^trazabilidad_reporte/filter-trazabilidad/$',
   r'^trazabilidad_reporte/trazabilidad-generate-report/(?P<pallet>[0-9]+)/$',

   #exit_reportes
   r'^exit_reportes/$',
   r'^exit_reportes/filter-exit/$',
   r'^exit_reportes/exit_generate_report/$',
   r'^exit_reportes/generate_exit_pdf_report/$',
   r'^exit_reportes/filter-exit-choices/(?P<field>\w+)$',
   #inventory_reportes
   r'^inventory_reportes/$',
   r'^inventory_reportes/filter-inventory/$',
   r'^inventory_reportes/inventory_generate_report/$',
   r'^inventory_reportes/inventory_pdf_generate_report/$',
   r'^inventory_reportes/filter-inventory-choices/(?P<field>\w+)$',

   #warehouse_occupacy
   r'^warehouse_ocupancy_reporte/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy-choices/(?P<field>\w+)$', 
   r'^warehouse_ocupancy_reporte/ocupancy_generate_report/$',
   r'^warehouse_ocupancy_reporte/generate_ocupancy_pdf_report/$',

   #Entrance Resumido Report
   r'^entradas_resumido_reporte/$',
   r'^entradas_resumido_reporte/filter-entrance-resumido/$',
   r'^entradas_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^entradas_resumido_reporte/generate_resumido_report/$',
   r'^entradas_resumido_reporte/generate_resumido_pdf/$',

   #exit Resumido Report
   r'^exit_resumido_reporte/$',
   r'^exit_resumido_reporte/filter-exit-resumido/$',
   r'^exit_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^exit_resumido_reporte/generate_resumido_report/$',
   r'^exit_resumido_reporte/generate_resumido_pdf/$',

   #Inventory Resumido Report
   r'^inventario_resumido_reporte/$',
   r'^inventario_resumido_reporte/inventario-resumido-filter/$',
   r'^inventario_resumido_reporte/generate_inventory_resumido_report/$', 
   r'^inventario_resumido_reporte/inventory_summary_generate_pdf/$',

   #inventory Log Report
   r'^inventory_reportes/inventory_log_list/',
   r'^inventory_reportes/filter-inventory-log/',
   r'^inventory_reportes/generate_inv_log_report/',
   r'^inventory_reportes/generate_inv_log_pdf/',

   # ------- New process started -----------
   #------new maniobras process started ---------
   r'^maneuver/get-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/save-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-entrances-list$',
   r'^maneuver/maniobras-entrance-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-exit-list$',
   r'^maneuver/maniobras-exit-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consolidate$',
   r'^maneuver/get-inventory-detail$',
   r'^maneuver/save-consolidate$',
   r'^warehouse_relocation/relocation-shortcode-weight-volume/$',
   r'^warehouse_relocation/save-relocation-from-shortcode/$',
   r'^warehouses/warehouse/get-warehouse-location-detail$',
   r'^warehouse_relocation/relocation-exit-shortcode-weight-volume/$',   
   r'^warehouse_relocation/save-exit-relocation-from-shortcode/',
   #------new maniobras process ended -----------

   # ------- New Exit process started -----------
   r'^warehouse_exit/$',
   r'^warehouse_exit/new-warehouse-exit-list$',
   r'^warehouse_exit/new-warehouse-exit$',
   r'^warehouse_exit/new-update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/auto-print-picking$',
   r'^warehouse_exit/confirm-warehouse-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/confirm-exit-pallet/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-print-picking/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-detail-for-relocation$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/exit-resultado-romaneo/$',
   # ------- New Exit process ended -----------------

   # ------- New Entrance process started -----------
   r'^warehouse_entrance/entrance-new$',
   r'^warehouse_entrance/entrances-list$',
   r'^warehouse_entrance/edit-entrance/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/entrance-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/new-confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/save-pallet-measurement$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   r'^warehouse_entrance/get-single-pallet-detail$',
   r'^warehouse_entrance/save-pallet-location$',
   r'^warehouse_entrance/get-pallet-from-entrance$',
   r'^warehouse_entrance/get-prev-next-pallet$',
   r'^warehouse_entrance/entrance-pallet-detail-for-relocation$',
   r'^warehouse_entrance/new-entrance-confirmation/(?P<pk>[0-9]+)$',   
   r'^warehouse_entrance/compare-box-total-kg/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/entrance-resultado-romaneo/$',
   r'^inventory_reportes/resultado-de-romaneo/',
   r'^inventory_reportes/resultado-de-romaneo-report/',
   r'^inventory_reserve/$',
   r'^inventory_reserve/add$',
   r'^inventory_reserve/(?P<pk>[0-9]+)/$',
   r'^inventory_reserve/inventory_filter_list$',
   r'^inventory_reserve/release_reserved_inventory$',
   # ------- New Entrance process ended ----------

   # ------- New Requirement Details -------------

   r'^media/*',
   r'^warehouses/branches$',
   )


#JAFEALMACEN Login Url
JAFEALMACEN_LOGIN_URLS = (
   r'^$',
   r'^/login/$',
   r'^api/notifications/$',
   r'^notifications/update-status/(?P<pk>[0-9]+)$',
   #product
   r'^product/$',
   r'^product/add$',
   r'^product/(?P<pk>[0-9]+)/$', 
   r'^product/(?P<pk>[0-9]+)/delete/$',
   r'^product-update/$',
   # #warehouses
   # r'^warehouses/warehouse/$',
   # r'^warehouses/warehouse/add$',
   # r'^warehouses/warehouse/(?P<pk>[0-9]+)/$',
   # r'^warehouses/warehouse/(?P<pk>[0-9]+)/delete/$',
   # r'^warehouses/warehouse-location/(?P<pk>[0-9]+)/delete/$',
   # r'^warehouses/warehouseproduct-filter/(?P<pk>[0-9]+)/$',
   # r'^warehouses/warehouselocation-product/(?P<warehouse>[0-9]+)/(?P<location>[0-9]+)/(?P<customer>[0-9]+)$',
  
   #inventory_reserve  
   r'^inventory_reserve/$',
   r'^inventory_reserve/add$',
   r'^inventory_reserve/(?P<pk>[0-9]+)/$',
   r'^inventory_reserve/inventory_filter_list$',
   r'^inventory_reserve/release_reserved_inventory$',

   #Entrance
   r'^warehouse_entrance/customer-products/(?P<pk>[\w]+)/$',
   r'^warehouse_exit/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/$',
   r'^warehouse_entrance/add$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_entrance/customer-products/(?P<pk>[\w]+)/$',
   r'^warehouse_entrance/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/download-entrace-invoice/$',
   r'^warehouse_entrance/get-rack/(?P<warehouse>[0-9]+)/$',
   r'^warehouse_entrance/get-location/$',
   r'^warehouse_entrance/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_entrance/save-pallet-peso-variable$',
   r'^warehouse_entrance/save-romaneo-product-weight$',
   r'^warehouse_entrance/save-entrance-pallet$',
   r'^warehouse_entrance/get-entrance-palet-qrcode$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/check-print-picking$',
   r'^warehouse_entrance/save-romaneo-peso-variables/(?P<pk>[0-9]+)$',
   r'^menuover_login_validation',   

    #warehouse_exit
   r'^warehouse_exit/$',
   r'^warehouse_exit/add$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_exit/warehouse-location/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-location-detail/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-location-detail/$',
   r'^warehouse_exit/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/download-exit-invoice/$',
   r'^warehouse_exit/exit_filter_for_location/$',
   r'^warehouse_exit/print-picking/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/auto-picking$',
   r'^warehouse_exit/save-exit-pallet$',
   r'^warehouse_exit/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_exit/save-pallet-peso-variable$',
   r'^warehouse_exit/exit-save-romaneo-product-weight$',
   r'^warehouse_entrance/save-romaneo-product-weight$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
  
   # ------- New process started -----------
   #------new maniobras process started ---------
   r'^maneuver/get-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/save-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-entrances-list$',
   r'^maneuver/maniobras-entrance-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-exit-list$',
   r'^maneuver/maniobras-exit-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consolidate$',
   r'^maneuver/get-inventory-detail$',
   r'^maneuver/save-consolidate$',
   r'^warehouse_relocation/relocation-shortcode-weight-volume/$',
   r'^warehouse_relocation/save-relocation-from-shortcode/$',
   r'^warehouses/warehouse/get-warehouse-location-detail$',
   r'^warehouse_relocation/relocation-exit-shortcode-weight-volume/$',   
   r'^warehouse_relocation/save-exit-relocation-from-shortcode/',
   #------new maniobras process ended -----------

   # ------- New Exit process started -----------
   r'^warehouse_exit/$',
   r'^warehouse_exit/new-warehouse-exit-list$',
   r'^warehouse_exit/new-warehouse-exit$',
   r'^warehouse_exit/new-update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/auto-print-picking$',
   r'^warehouse_exit/confirm-warehouse-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/confirm-exit-pallet/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-print-picking/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-detail-for-relocation$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/exit-resultado-romaneo/$',
   # ------- New Exit process ended -----------------

   # ------- New Entrance process started -----------
   r'^warehouse_entrance/entrance-new$',
   r'^warehouse_entrance/entrances-list$',
   r'^warehouse_entrance/edit-entrance/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/entrance-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/new-confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/save-pallet-measurement$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   r'^warehouse_entrance/get-single-pallet-detail$',
   r'^warehouse_entrance/save-pallet-location$',
   r'^warehouse_entrance/get-pallet-from-entrance$',
   r'^warehouse_entrance/get-prev-next-pallet$',
   r'^warehouse_entrance/entrance-pallet-detail-for-relocation$',
   r'^warehouse_entrance/new-entrance-confirmation/(?P<pk>[0-9]+)$',   
   r'^warehouse_entrance/compare-box-total-kg/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/entrance-resultado-romaneo/$',
   r'^inventory_reportes/resultado-de-romaneo/',
   r'^inventory_reportes/resultado-de-romaneo-report/',
   # ------- New Entrance process ended ----------

   # ------- New Requirement Details -------------

   #new changes
   r'^warehouse_entrance/warehouse-entrances-list$',
   r'^warehouse_entrance/new-entrance$',
   r'^warehouse_entrance/confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/update-entrance/(?P<pk>[0-9]+)$',
   #new changes
   r'^warehouse_exit/warehouse-exit-list$',
   r'^warehouse_exit/new-exit$',
   r'^warehouse_exit/confirm-exit-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/clear-sessions$',

   #warehouse_history
   r'^warehouse_history/$',
   r'^warehouse_history/warehouse-history/$',


   #maniobras
   r'^maneuver/pallet-consult$',
   r'^warehouse_entrance/get-pallet-detail/(?P<pk>[0-9]+)/$',
   r'^maneuver/inventory_taking$',
   r'^maneuver/add-inventory-taking$',
   r'^maneuver/update-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/show-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/report-inventory-taking/(?P<pk>[0-9]+)/$',

   #location_management
   r'^location_management/$',
   r'^location_management/warehouse-location-manage/(?P<pk>[0-9]+)/$',   
   #warehouse_relocation
   r'^warehouse_relocation/$',
   r'^warehouse_relocation/add$',
   r'^warehouse_relocation/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_relocation/relocation-api/$',   
   r'^warehouse_relocation/warehouse/(?P<pk>[\w]+)/locations$',
   r'^warehouse_relocation/relocation-filter$',
   r'^warehouse_relocation/entrance-confirmation-product/(?P<entrance>[0-9]+)/(?P<product>[0-9]+)/(?P<customer>[0-9]+)$',
   r'^warehouse_relocation/relocation-destination-weight-volume/$',

   #entrance_reportes
   r'^entrance_reportes/$',
   r'^entrance_reportes/filter-entrance/$',
   r'^entrance_reportes/generate_report/$',
   r'^entrance_reportes/filter-choices/(?P<field>\w+)$',
   r'^entrance_reportes/generate_pdf_report/$',
   r'^trazabilidad_reporte/$',
   r'^trazabilidad_reporte/filter-trazabilidad/$',
   r'^trazabilidad_reporte/trazabilidad-generate-report/(?P<pallet>[0-9]+)/$',

   #exit_reportes
   r'^exit_reportes/$',
   r'^exit_reportes/filter-exit/$',
   r'^exit_reportes/exit_generate_report/$',
   r'^exit_reportes/filter-exit-choices/(?P<field>\w+)$',
   r'^exit_reportes/generate_exit_pdf_report/$',


 #inventory_reportes
   r'^inventory_reportes/$',
   r'^inventory_reportes/filter-inventory/$',
   r'^inventory_reportes/inventory_generate_report/$',
   r'^inventory_reportes/inventory_pdf_generate_report/$',
   r'^inventory_reportes/filter-inventory-choices/(?P<field>\w+)$',


   #warehouse_occupacy
   r'^warehouse_ocupancy_reporte/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy-choices/(?P<field>\w+)$', 
   r'^warehouse_ocupancy_reporte/ocupancy_generate_report/$',
   r'^warehouse_ocupancy_reporte/generate_ocupancy_pdf_report/$',

   #Entrance Resumido Report
   r'^entradas_resumido_reporte/$',
   r'^entradas_resumido_reporte/filter-entrance-resumido/$',
   r'^entradas_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^entradas_resumido_reporte/generate_resumido_report/$',
   r'^entradas_resumido_reporte/generate_resumido_pdf/$',

   #exit Resumido Report
   r'^exit_resumido_reporte/$',
   r'^exit_resumido_reporte/filter-exit-resumido/$',
   r'^exit_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^exit_resumido_reporte/generate_resumido_report/$',
   r'^exit_resumido_reporte/generate_resumido_pdf/$',



   #Inventory Resumido Report
   r'^inventario_resumido_reporte/$',
   r'^inventario_resumido_reporte/inventario-resumido-filter/$',
   r'^inventario_resumido_reporte/generate_inventory_resumido_report/$', 
   r'^inventario_resumido_reporte/inventory_summary_generate_pdf/$',

   #inventory Log Report
   r'^inventory_reportes/inventory_log_list/',
   r'^inventory_reportes/filter-inventory-log/',
   r'^inventory_reportes/generate_inv_log_report/',
   r'^inventory_reportes/generate_inv_log_pdf/',

    #maneuver menu
   r'^maneuver/entrances-list$',
   r'^maneuver/exit-list$',
   r'^maneuver/confirm-entrance_pallet/(?P<pk>[0-9]+)$',
   r'^maneuver/confirm-exit_pallet/(?P<pk>[0-9]+)$',
   r'^maneuver/entrance-update/(?P<pk>[0-9]+)$',
   r'^maneuver/exit-update/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consult$',
   r'^warehouse_entrance/get-pallet-detail/(?P<pk>[0-9]+)/$',
   r'^maneuver/inventory_taking$',
   r'^maneuver/add-inventory-taking$',
   r'^maneuver/update-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/show-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/report-inventory-taking/(?P<pk>[0-9]+)/$',

   r'^media/*',
   r'^warehouses/branches$',
   )


#INVENTORY Login Url
INVENTORY_LOGIN_URLS = (
   r'^$',
   r'^/login/$',
   
   r'^warehouse_entrance/customer-products/(?P<pk>[\w]+)/$',
   r'^warehouse_exit/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   #warehouse_history
   r'^warehouse_history/$',
   r'^warehouse_history/warehouse-history/$',

   #location_management
   r'^location_management/$',
   r'^location_management/warehouse-location-manage/(?P<pk>[0-9]+)/$',   
   #warehouse_relocation
   r'^warehouse_relocation/$',
   r'^warehouse_relocation/add$',
   r'^warehouse_relocation/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_relocation/relocation-api/$',   
   r'^warehouse_relocation/warehouse/(?P<pk>[\w]+)/locations$',
   r'^warehouse_relocation/relocation-filter$',
   r'^warehouse_relocation/entrance-confirmation-product/(?P<entrance>[0-9]+)/(?P<product>[0-9]+)/(?P<customer>[0-9]+)$',
   r'^warehouse_relocation/relocation-destination-weight-volume/$',

   #maniobras
   r'^maneuver/pallet-consult$',
   r'^warehouse_entrance/get-pallet-detail/(?P<pk>[0-9]+)/$',
   r'^maneuver/inventory_taking$',
   r'^maneuver/add-inventory-taking$',
   r'^maneuver/update-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/show-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/report-inventory-taking/(?P<pk>[0-9]+)/$',

   #entrance_reportes
   r'^entrance_reportes/$',
   r'^entrance_reportes/filter-entrance/$',
   r'^entrance_reportes/generate_report/$',
   r'^entrance_reportes/generate_pdf_report/$',
   r'^entrance_reportes/filter-choices/(?P<field>\w+)$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   r'^trazabilidad_reporte/$',
   r'^trazabilidad_reporte/filter-trazabilidad/$',
   r'^trazabilidad_reporte/trazabilidad-generate-report/(?P<pallet>[0-9]+)/$',

   #exit_reportes
   r'^exit_reportes/$',
   r'^exit_reportes/filter-exit/$',
   r'^exit_reportes/exit_generate_report/$',
   r'^exit_reportes/generate_exit_pdf_report/$',
   r'^exit_reportes/filter-exit-choices/(?P<field>\w+)$',
   #inventory_reportes
   r'^inventory_reportes/$',
   r'^inventory_reportes/filter-inventory/$',
   r'^inventory_reportes/inventory_generate_report/$',
   r'^inventory_reportes/inventory_pdf_generate_report/$',
   r'^inventory_reportes/inventory_pdf_generate_report/$',
   r'^inventory_reportes/filter-inventory-choices/(?P<field>\w+)$',

   #warehouse_occupacy
   r'^warehouse_ocupancy_reporte/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy-choices/(?P<field>\w+)$', 
   r'^warehouse_ocupancy_reporte/ocupancy_generate_report/$',
   r'^warehouse_ocupancy_reporte/generate_ocupancy_pdf_report/$',

   #Entrance Resumido Report
   r'^entradas_resumido_reporte/$',
   r'^entradas_resumido_reporte/filter-entrance-resumido/$',
   r'^entradas_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^entradas_resumido_reporte/generate_resumido_report/$',
   r'^entradas_resumido_reporte/generate_resumido_pdf/$',

   #exit Resumido Report
   r'^exit_resumido_reporte/$',
   r'^exit_resumido_reporte/filter-exit-resumido/$',
   r'^exit_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^exit_resumido_reporte/generate_resumido_report/$',
   r'^exit_resumido_reporte/generate_resumido_pdf/$',

   #Inventory Resumido Report
   r'^inventario_resumido_reporte/$',
   r'^inventario_resumido_reporte/inventario-resumido-filter/$',
   r'^inventario_resumido_reporte/generate_inventory_resumido_report/$', 
   r'^inventario_resumido_reporte/inventory_summary_generate_pdf/$',

   #inventory Log Report
   r'^inventory_reportes/inventory_log_list/',
   r'^inventory_reportes/filter-inventory-log/',
   r'^inventory_reportes/generate_inv_log_report/',
   r'^inventory_reportes/generate_inv_log_pdf/',
   r'^warehouse_exit/(?P<pk>[0-9]+)/check-print-picking$',
   r'^warehouse_entrance/save-romaneo-peso-variables/(?P<pk>[0-9]+)$',

   # ------- New process started -----------
   #------new maniobras process started ---------
   r'^maneuver/get-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/save-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-entrances-list$',
   r'^maneuver/maniobras-entrance-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-exit-list$',
   r'^maneuver/maniobras-exit-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consolidate$',
   r'^maneuver/get-inventory-detail$',
   r'^maneuver/save-consolidate$',
   r'^warehouse_relocation/relocation-shortcode-weight-volume/$',
   r'^warehouse_relocation/save-relocation-from-shortcode/$',
   r'^warehouses/warehouse/get-warehouse-location-detail$',
   r'^warehouse_relocation/relocation-exit-shortcode-weight-volume/$',   
   r'^warehouse_relocation/save-exit-relocation-from-shortcode/',
   #------new maniobras process ended -----------

   # ------- New Exit process started -----------
   r'^warehouse_exit/$',
   r'^warehouse_exit/new-warehouse-exit-list$',
   r'^warehouse_exit/new-warehouse-exit$',
   r'^warehouse_exit/new-update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/auto-print-picking$',
   r'^warehouse_exit/confirm-warehouse-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/confirm-exit-pallet/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-print-picking/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-detail-for-relocation$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/exit-resultado-romaneo/$',
   # ------- New Exit process ended -----------------

   # ------- New Entrance process started -----------
   r'^warehouse_entrance/entrance-new$',
   r'^warehouse_entrance/entrances-list$',
   r'^warehouse_entrance/edit-entrance/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/entrance-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/new-confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/save-pallet-measurement$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   r'^warehouse_entrance/get-single-pallet-detail$',
   r'^warehouse_entrance/save-pallet-location$',
   r'^warehouse_entrance/get-pallet-from-entrance$',
   r'^warehouse_entrance/get-prev-next-pallet$',
   r'^warehouse_entrance/entrance-pallet-detail-for-relocation$',
   r'^warehouse_entrance/new-entrance-confirmation/(?P<pk>[0-9]+)$',   
   r'^warehouse_entrance/compare-box-total-kg/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/entrance-resultado-romaneo/$',
   r'^inventory_reportes/resultado-de-romaneo/',
   r'^inventory_reportes/resultado-de-romaneo-report/',
   r'^inventory_reserve/$',
   r'^inventory_reserve/add$',
   r'^inventory_reserve/(?P<pk>[0-9]+)/$',
   r'^inventory_reserve/inventory_filter_list$',
   r'^inventory_reserve/release_reserved_inventory$',
   # ------- New Entrance process ended ----------

   # ------- New Requirement Details -------------

   r'^media/*',
   )


#JAFAADMINISTRATION Login Url
JAFAADMINISTRATION_LOGIN_URLS = (
   r'^$',
   r'^/login/$',
   r'^api/notifications/$',
   r'^notifications/update-status/(?P<pk>[0-9]+)$',

   #warehouses
   # r'^warehouses/warehouse/$',
   # r'^warehouses/warehouse/add$',
   # r'^warehouses/warehouse/(?P<pk>[0-9]+)/$',
   # r'^warehouses/warehouse/(?P<pk>[0-9]+)/delete/$',
   # r'^warehouses/warehouse-location/(?P<pk>[0-9]+)/delete/$',
   # r'^warehouses/warehouseproduct-filter/(?P<pk>[0-9]+)/$',
   # r'^warehouses/warehouselocation-product/(?P<warehouse>[0-9]+)/(?P<location>[0-9]+)/(?P<customer>[0-9]+)$',
   

   #packaging
   r'^packaging/$',
   r'^packaging/add$',
   r'^packaging/(?P<pk>[0-9]+)/$', 
   r'^packaging/(?P<pk>[0-9]+)/delete/$',

   #product
   r'^product/$',
   r'^product/add$',
   r'^product/(?P<pk>[0-9]+)/$', 
   r'^product/(?P<pk>[0-9]+)/delete/$',
   r'^product-update/$',

   #unit
   r'^unit/$',
   r'^unit/add$',
   r'^unit/(?P<pk>[0-9]+)/$', 
   r'^unit/(?P<pk>[0-9]+)/delete/$',

   #productfamily
   r'^productfamily/$',
   r'^productfamily/add$',
   r'^productfamily/(?P<pk>[0-9]+)/$', 
   r'^productfamily/(?P<pk>[0-9]+)/delete/$',

   #vehicles
   r'^vehicles/$',
   r'^vehicles/add$',
   r'^vehicles/(?P<pk>[0-9]+)/$', 
   r'^vehicles/(?P<pk>[0-9]+)/delete/$',

   #carriers
   r'^carriers/$',
   r'^carriers/add$',
   r'^carriers/(?P<pk>[0-9]+)/$', 
   r'^carriers/(?P<pk>[0-9]+)/delete/$',

   #consigees
   r'^consigees/$',
   r'^consigees/add$',
   r'^consigees/(?P<pk>[0-9]+)/$', 
   r'^consigees/(?P<pk>[0-9]+)/delete/$',

   r'^client/$',
   r'^client/add$',
   r'^client/(?P<pk>[0-9]+)/$',
   r'^client/(?P<pk>[0-9]+)/delete/$',

   #warehouse_entrance
   r'^warehouse_entrance/$',
   r'^warehouse_entrance/add$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_entrance/customer-products/(?P<pk>[\w]+)/$',
   r'^warehouse_entrance/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/download-entrace-invoice/$',
   r'^warehouse_entrance/get-rack/(?P<warehouse>[0-9]+)/$',
   r'^warehouse_entrance/get-location/$',
   r'^warehouse_entrance/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_entrance/save-pallet-peso-variable$',
   r'^warehouse_entrance/save-entrance-pallet$',
   r'^warehouse_entrance/get-entrance-palet-qrcode$',
   r'^warehouse_entrance/save-romaneo-product-weight$',
   r'^warehouse_entrance/check-peso-variables-quantity$',

   r'^warehouse_exit/(?P<pk>[0-9]+)/check-print-picking$',
   r'^warehouse_entrance/save-romaneo-peso-variables/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
    #warehouse_exit
   r'^warehouse_exit/$',
   r'^warehouse_exit/add$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_exit/warehouse-location/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-location-detail/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-location-detail/$',
   r'^warehouse_exit/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/download-exit-invoice/$',
   r'^warehouse_exit/exit_filter_for_location/$',
   r'^warehouse_exit/print-picking/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/auto-picking$',
   r'^warehouse_exit/save-exit-pallet$',
   r'^warehouse_exit/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_exit/save-pallet-peso-variable$',
   r'^warehouse_exit/exit-save-romaneo-product-weight$',

   #new changes
   r'^warehouse_entrance/warehouse-entrances-list$',
   r'^warehouse_entrance/new-entrance$',
   r'^warehouse_entrance/confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/update-entrance/(?P<pk>[0-9]+)$',
   #new changes
   r'^warehouse_exit/warehouse-exit-list$',
   r'^warehouse_exit/new-exit$',
   r'^warehouse_exit/confirm-exit-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/clear-sessions$',

   #maniobras
   r'^maneuver/pallet-consult$',
   r'^warehouse_entrance/get-pallet-detail/(?P<pk>[0-9]+)/$',
   r'^maneuver/inventory_taking$',
   r'^maneuver/add-inventory-taking$',
   r'^maneuver/update-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/show-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/report-inventory-taking/(?P<pk>[0-9]+)/$',

   #location_management
   r'^location_management/$',
   r'^location_management/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   #warehouse_history
   r'^warehouse_history/$',
   r'^warehouse_history/warehouse-history/$',
      #warehouse_relocation
   r'^warehouse_relocation/$',
   r'^warehouse_relocation/add$',
   r'^warehouse_relocation/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_relocation/relocation-api/$',   
   r'^warehouse_relocation/warehouse/(?P<pk>[\w]+)/locations$',
   r'^warehouse_relocation/relocation-filter$',
   r'^warehouse_relocation/entrance-confirmation-product/(?P<entrance>[0-9]+)/(?P<product>[0-9]+)/(?P<customer>[0-9]+)$',
   r'^warehouse_relocation/relocation-destination-weight-volume/$',

   #entrance_reportes
   r'^entrance_reportes/$',
   r'^entrance_reportes/filter-entrance/$',
   r'^entrance_reportes/generate_report/$',
   r'^entrance_reportes/generate_pdf_report/$',
   r'^entrance_reportes/filter-choices/(?P<field>\w+)$',
   r'^trazabilidad_reporte/$',
   r'^trazabilidad_reporte/filter-trazabilidad/$',
   r'^trazabilidad_reporte/trazabilidad-generate-report/(?P<pallet>[0-9]+)/$',
 
   #exit_reportes
   r'^exit_reportes/$',
   r'^exit_reportes/filter-exit/$',
   r'^exit_reportes/exit_generate_report/$',
   r'^exit_reportes/generate_exit_pdf_report/$',
   r'^exit_reportes/filter-exit-choices/(?P<field>\w+)$',
   #inventory_reportes
   r'^inventory_reportes/$',
   r'^inventory_reportes/filter-inventory/$',
   r'^inventory_reportes/inventory_generate_report/$',
   r'^inventory_reportes/inventory_pdf_generate_report/$',
   r'^inventory_reportes/filter-inventory-choices/(?P<field>\w+)$',

   #warehouse_occupacy
   r'^warehouse_ocupancy_reporte/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy-choices/(?P<field>\w+)$', 
   r'^warehouse_ocupancy_reporte/ocupancy_generate_report/$',
   r'^warehouse_ocupancy_reporte/generate_ocupancy_pdf_report/$',

   #Entrance Resumido Report
   r'^entradas_resumido_reporte/$',
   r'^entradas_resumido_reporte/filter-entrance-resumido/$',
   r'^entradas_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^entradas_resumido_reporte/generate_resumido_report/$',
   r'^entradas_resumido_reporte/generate_resumido_pdf/$',

   #exit Resumido Report
   r'^exit_resumido_reporte/$',
   r'^exit_resumido_reporte/filter-exit-resumido/$',
   r'^exit_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^exit_resumido_reporte/generate_resumido_report/$',
   r'^exit_resumido_reporte/generate_resumido_pdf/$',

   #Inventory Resumido Report
   r'^inventario_resumido_reporte/$',
   r'^inventario_resumido_reporte/inventario-resumido-filter/$',
   r'^inventario_resumido_reporte/generate_inventory_resumido_report/$', 
   r'^inventario_resumido_reporte/inventory_summary_generate_pdf/$',

   # ------- New process started -----------
   #------new maniobras process started ---------
   r'^maneuver/get-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/save-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-entrances-list$',
   r'^maneuver/maniobras-entrance-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-exit-list$',
   r'^maneuver/maniobras-exit-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consolidate$',
   r'^maneuver/get-inventory-detail$',
   r'^maneuver/save-consolidate$',
   r'^warehouse_relocation/relocation-shortcode-weight-volume/$',
   r'^warehouse_relocation/save-relocation-from-shortcode/$',
   r'^warehouses/warehouse/get-warehouse-location-detail$',
   r'^warehouse_relocation/relocation-exit-shortcode-weight-volume/$',   
   r'^warehouse_relocation/save-exit-relocation-from-shortcode/',
   #------new maniobras process ended -----------

   # ------- New Exit process started -----------
   r'^warehouse_exit/$',
   r'^warehouse_exit/new-warehouse-exit-list$',
   r'^warehouse_exit/new-warehouse-exit$',
   r'^warehouse_exit/new-update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/auto-print-picking$',
   r'^warehouse_exit/confirm-warehouse-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/confirm-exit-pallet/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-print-picking/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-detail-for-relocation$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/exit-resultado-romaneo/$',
   # ------- New Exit process ended -----------------

   # ------- New Entrance process started -----------
   r'^warehouse_entrance/entrance-new$',
   r'^warehouse_entrance/entrances-list$',
   r'^warehouse_entrance/edit-entrance/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/entrance-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/new-confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/save-pallet-measurement$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   r'^warehouse_entrance/get-single-pallet-detail$',
   r'^warehouse_entrance/save-pallet-location$',
   r'^warehouse_entrance/get-pallet-from-entrance$',
   r'^warehouse_entrance/get-prev-next-pallet$',
   r'^warehouse_entrance/entrance-pallet-detail-for-relocation$',
   r'^warehouse_entrance/new-entrance-confirmation/(?P<pk>[0-9]+)$',   
   r'^warehouse_entrance/compare-box-total-kg/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/entrance-resultado-romaneo/$',
   r'^inventory_reportes/resultado-de-romaneo/',
   r'^inventory_reportes/resultado-de-romaneo-report/',
   r'^inventory_reserve/$',
   r'^inventory_reserve/add$',
   r'^inventory_reserve/(?P<pk>[0-9]+)/$',
   r'^inventory_reserve/inventory_filter_list$',
   r'^inventory_reserve/release_reserved_inventory$',
   # ------- New Entrance process ended ----------

   # ------- New Requirement Details -------------

   r'^media/*',   
   )


#CONTROL Login Url
CONTROL_LOGIN_URLS = (
   r'^$',
   r'^/login/$',
   
    #warehouse_entrance
   r'^warehouse_entrance/$',
   r'^warehouse_entrance/add$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_entrance/customer-products/(?P<pk>[\w]+)/$',
   r'^warehouse_entrance/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/download-entrace-invoice/$',
   r'^warehouse_entrance/get-rack/(?P<warehouse>[0-9]+)/$',
   r'^warehouse_entrance/get-location/$',
   r'^warehouse_entrance/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_entrance/save-pallet-peso-variable$',
   r'^warehouse_entrance/save-entrance-pallet$',
   r'^warehouse_entrance/get-entrance-palet-qrcode$',
   r'^warehouse_entrance/save-romaneo-product-weight$',
   r'^warehouse_entrance/check-peso-variables-quantity$',

   #warehouse_exit
   r'^warehouse_exit/$',
   r'^warehouse_exit/add$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_exit/warehouse-location/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-location-detail/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-location-detail/$',
   r'^warehouse_exit/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/download-exit-invoice/$',
   r'^warehouse_exit/exit_filter_for_location/$',
   r'^warehouse_exit/print-picking/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/auto-picking$',
   r'^warehouse_exit/save-exit-pallet$',
   r'^warehouse_exit/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_exit/save-pallet-peso-variable$',
   r'^warehouse_exit/exit-save-romaneo-product-weight$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/check-print-picking$',
   r'^warehouse_entrance/save-romaneo-peso-variables/(?P<pk>[0-9]+)$',
   #new changes
   r'^warehouse_entrance/warehouse-entrances-list$',
   r'^warehouse_entrance/new-entrance$',
   r'^warehouse_entrance/confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/update-entrance/(?P<pk>[0-9]+)$',
   #new changes
   r'^warehouse_exit/warehouse-exit-list$',
   r'^warehouse_exit/new-exit$',
   r'^warehouse_exit/confirm-exit-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/clear-sessions$',

   #location_management
   r'^location_management/$',
   r'^location_management/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   #warehouse_history
   r'^warehouse_history/$',
   r'^warehouse_history/warehouse-history/$',
   #warehouse_relocation
   r'^warehouse_relocation/$',
   r'^warehouse_relocation/add$',
   r'^warehouse_relocation/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_relocation/relocation-api/$',   
   r'^warehouse_relocation/warehouse/(?P<pk>[\w]+)/locations$',
   r'^warehouse_relocation/relocation-filter$',
   r'^warehouse_relocation/entrance-confirmation-product/(?P<entrance>[0-9]+)/(?P<product>[0-9]+)/(?P<customer>[0-9]+)$',
   r'^warehouse_relocation/relocation-destination-weight-volume/$',

   #maniobras
   r'^maneuver/pallet-consult$',
   r'^warehouse_entrance/get-pallet-detail/(?P<pk>[0-9]+)/$',
   r'^maneuver/inventory_taking$',
   r'^maneuver/add-inventory-taking$',
   r'^maneuver/update-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/show-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/report-inventory-taking/(?P<pk>[0-9]+)/$',

   #entrance_reportes
   r'^entrance_reportes/$',
   r'^entrance_reportes/filter-entrance/$',
   r'^entrance_reportes/generate_report/$',
   r'^entrance_reportes/generate_pdf_report/$',
   r'^entrance_reportes/filter-choices/(?P<field>\w+)$',

   r'^trazabilidad_reporte/$',
   r'^trazabilidad_reporte/filter-trazabilidad/$',
   r'^trazabilidad_reporte/trazabilidad-generate-report/(?P<pallet>[0-9]+)/$',
   #exit_reportes
   r'^exit_reportes/$',
   r'^exit_reportes/filter-exit/$',
   r'^exit_reportes/exit_generate_report/$',
   r'^exit_reportes/generate_exit_pdf_report/$',
   r'^exit_reportes/filter-exit-choices/(?P<field>\w+)$',

   #inventory_reportes
   r'^inventory_reportes/$',
   r'^inventory_reportes/filter-inventory/$',
   r'^inventory_reportes/inventory_generate_report/$',
   r'^inventory_reportes/inventory_pdf_generate_report/$',      
   r'^inventory_reportes/filter-inventory-choices/(?P<field>\w+)$',

   #warehouse_occupacy
   r'^warehouse_ocupancy_reporte/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy/$',
   r'^warehouse_ocupancy_reporte/filter-ocupancy-choices/(?P<field>\w+)$', 
   r'^warehouse_ocupancy_reporte/ocupancy_generate_report/$',
   r'^warehouse_ocupancy_reporte/generate_ocupancy_pdf_report/$',

   #Entrance Resumido Report
   r'^entradas_resumido_reporte/$',
   r'^entradas_resumido_reporte/filter-entrance-resumido/$',
   r'^entradas_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^entradas_resumido_reporte/generate_resumido_report/$',
   r'^entradas_resumido_reporte/generate_resumido_pdf/$',

   #exit Resumido Report
   r'^exit_resumido_reporte/$',
   r'^exit_resumido_reporte/filter-exit-resumido/$',
   r'^exit_resumido_reporte/filter-resumido-choices/(?P<field>\w+)$', 
   r'^exit_resumido_reporte/generate_resumido_report/$',
   r'^exit_resumido_reporte/generate_resumido_pdf/$',

   #inventory Log Report
   r'^inventory_reportes/inventory_log_list/',
   r'^inventory_reportes/filter-inventory-log/',
   r'^inventory_reportes/generate_inv_log_report/',
   r'^inventory_reportes/generate_inv_log_pdf/',

   #Inventory Resumido Report
   r'^inventario_resumido_reporte/$',
   r'^inventario_resumido_reporte/inventario-resumido-filter/$',
   r'^inventario_resumido_reporte/generate_inventory_resumido_report/$', 
   r'^inventario_resumido_reporte/inventory_summary_generate_pdf/$',

   # ------- New process started -----------
   #------new maniobras process started ---------
   r'^maneuver/get-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/save-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-entrances-list$',
   r'^maneuver/maniobras-entrance-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-exit-list$',
   r'^maneuver/maniobras-exit-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consolidate$',
   r'^maneuver/get-inventory-detail$',
   r'^maneuver/save-consolidate$',
   r'^warehouse_relocation/relocation-shortcode-weight-volume/$',
   r'^warehouse_relocation/save-relocation-from-shortcode/$',
   r'^warehouses/warehouse/get-warehouse-location-detail$',
   r'^warehouse_relocation/relocation-exit-shortcode-weight-volume/$',   
   r'^warehouse_relocation/save-exit-relocation-from-shortcode/',
   #------new maniobras process ended -----------

   # ------- New Exit process started -----------
   r'^warehouse_exit/$',
   r'^warehouse_exit/new-warehouse-exit-list$',
   r'^warehouse_exit/new-warehouse-exit$',
   r'^warehouse_exit/new-update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/auto-print-picking$',
   r'^warehouse_exit/confirm-warehouse-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/confirm-exit-pallet/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-print-picking/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-detail-for-relocation$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/exit-resultado-romaneo/$',
   # ------- New Exit process ended -----------------

   # ------- New Entrance process started -----------
   r'^warehouse_entrance/entrance-new$',
   r'^warehouse_entrance/entrances-list$',
   r'^warehouse_entrance/edit-entrance/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/entrance-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/new-confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/save-pallet-measurement$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   r'^warehouse_entrance/get-single-pallet-detail$',
   r'^warehouse_entrance/save-pallet-location$',
   r'^warehouse_entrance/get-pallet-from-entrance$',
   r'^warehouse_entrance/get-prev-next-pallet$',
   r'^warehouse_entrance/entrance-pallet-detail-for-relocation$',
   r'^warehouse_entrance/new-entrance-confirmation/(?P<pk>[0-9]+)$',   
   r'^warehouse_entrance/compare-box-total-kg/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/entrance-resultado-romaneo/$',
   r'^inventory_reportes/resultado-de-romaneo/',
   r'^inventory_reportes/resultado-de-romaneo-report/',
   r'^inventory_reserve/$',
   r'^inventory_reserve/add$',
   r'^inventory_reserve/(?P<pk>[0-9]+)/$',
   r'^inventory_reserve/inventory_filter_list$',
   r'^inventory_reserve/release_reserved_inventory$',
   # ------- New Entrance process ended ----------

   # ------- New Requirement Details -------------

   r'^media/*',
   )






#CONTROL Login Url
WAREHOUSESHIFTSUPERVISOR_LOGIN_URLS = (
   r'^$',
   r'^/login/$',
   r'^api/notifications/$',
   r'^notifications/update-status/(?P<pk>[0-9]+)$',   
    #warehouse_entrance
   r'^warehouse_entrance/$',
   r'^warehouse_entrance/add$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_entrance/customer-products/(?P<pk>[\w]+)/$',
   r'^warehouse_entrance/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/download-entrace-invoice/$',
   r'^warehouse_entrance/get-rack/(?P<warehouse>[0-9]+)/$',
   r'^warehouse_entrance/get-location/$',
   r'^warehouse_entrance/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_entrance/save-pallet-peso-variable$',
   r'^warehouse_entrance/save-entrance-pallet$',
   r'^warehouse_entrance/get-entrance-palet-qrcode$',
   r'^warehouse_entrance/save-romaneo-product-weight$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   #warehouse_exit
   r'^warehouse_exit/$',
   r'^warehouse_exit/add$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/delete/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_exit/warehouse-location/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-location-detail/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-location-detail/$',
   r'^warehouse_exit/warehouse-location-manage/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-entrance-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/warehouse-exit-confirmation/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/download-exit-invoice/$',
   r'^warehouse_exit/exit_filter_for_location/$',
   r'^warehouse_exit/print-picking/(?P<pk>[0-9]+)/$',
   r'^warehouse_exit/auto-picking$',
   r'^warehouse_exit/save-exit-pallet$',
   r'^warehouse_exit/get-pallet-peso-variable/(?P<pallet>[0-9]+)/$',
   r'^warehouse_exit/save-pallet-peso-variable$',
   r'^warehouse_exit/exit-save-romaneo-product-weight$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/check-print-picking$',
   r'^warehouse_entrance/save-romaneo-peso-variables/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   #new changes
   r'^warehouse_entrance/warehouse-entrances-list$',
   r'^warehouse_entrance/new-entrance$',
   r'^warehouse_entrance/update-entrance/(?P<pk>[0-9]+)$',
   #new changes
   r'^warehouse_exit/warehouse-exit-list$',
   r'^warehouse_exit/new-exit$',
   r'^warehouse_exit/confirm-exit-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/clear-sessions$',
   
   #warehouse_relocation
   r'^warehouse_relocation/$',
   r'^warehouse_relocation/add$',
   r'^warehouse_relocation/(?P<pk>[0-9]+)/detail/$',
   r'^warehouse_relocation/relocation-api/$',   
   r'^warehouse_relocation/warehouse/(?P<pk>[\w]+)/locations$',
   r'^warehouse_relocation/relocation-filter$',
   r'^warehouse_relocation/entrance-confirmation-product/(?P<entrance>[0-9]+)/(?P<product>[0-9]+)/(?P<customer>[0-9]+)$',
   r'^warehouse_relocation/relocation-destination-weight-volume/$',
   
   #maneuver menu
   r'^maneuver/entrances-list$',
   r'^maneuver/exit-list$',
   r'^maneuver/confirm-entrance_pallet/(?P<pk>[0-9]+)$',
   r'^maneuver/confirm-exit_pallet/(?P<pk>[0-9]+)$',
   r'^maneuver/entrance-update/(?P<pk>[0-9]+)$',
   r'^maneuver/exit-update/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consult$',
   r'^warehouse_entrance/get-pallet-detail/(?P<pk>[0-9]+)/$',
   r'^maneuver/inventory_taking$',
   r'^maneuver/add-inventory-taking$',
   r'^maneuver/update-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/show-inventory-taking/(?P<pk>[0-9]+)$',
   r'^maneuver/report-inventory-taking/(?P<pk>[0-9]+)/$',
   
   # ------- New process started -----------
   #------new maniobras process started ---------
   r'^maneuver/get-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/save-inventory-peso-variable/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-entrances-list$',
   r'^maneuver/maniobras-entrance-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/maniobras-exit-list$',
   r'^maneuver/maniobras-exit-edit/(?P<pk>[0-9]+)$',
   r'^maneuver/pallet-consolidate$',
   r'^maneuver/get-inventory-detail$',
   r'^maneuver/save-consolidate$',
   r'^warehouse_relocation/relocation-shortcode-weight-volume/$',
   r'^warehouse_relocation/save-relocation-from-shortcode/$',
   r'^warehouses/warehouse/get-warehouse-location-detail$',
   r'^warehouse_relocation/relocation-exit-shortcode-weight-volume/$',   
   r'^warehouse_relocation/save-exit-relocation-from-shortcode/',
   #------new maniobras process ended -----------

   # ------- New Exit process started -----------
   r'^warehouse_exit/$',
   r'^warehouse_exit/new-warehouse-exit-list$',
   r'^warehouse_exit/new-warehouse-exit$',
   r'^warehouse_exit/new-update-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/auto-print-picking$',
   r'^warehouse_exit/confirm-warehouse-exit/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/confirm-exit-pallet/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-print-picking/(?P<pk>[0-9]+)$',
   r'^warehouse_exit/exit-pallet-detail-for-relocation$',
   r'^warehouse_exit/(?P<pk>[0-9]+)/exit-resultado-romaneo/$',
   # ------- New Exit process ended -----------------

   # ------- New Entrance process started -----------
   r'^warehouse_entrance/entrance-new$',
   r'^warehouse_entrance/entrances-list$',
   r'^warehouse_entrance/edit-entrance/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/entrance-pallet-details/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/new-confirm-entrance-pallets/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/save-pallet-measurement$',
   r'^warehouse_entrance/check-peso-variables-quantity$',
   r'^warehouse_entrance/get-single-pallet-detail$',
   r'^warehouse_entrance/save-pallet-location$',
   r'^warehouse_entrance/get-pallet-from-entrance$',
   r'^warehouse_entrance/get-prev-next-pallet$',
   r'^warehouse_entrance/entrance-pallet-detail-for-relocation$',
   r'^warehouse_entrance/new-entrance-confirmation/(?P<pk>[0-9]+)$',   
   r'^warehouse_entrance/compare-box-total-kg/(?P<pk>[0-9]+)$',
   r'^warehouse_entrance/(?P<pk>[0-9]+)/entrance-resultado-romaneo/$',
   r'^inventory_reportes/resultado-de-romaneo/',
   r'^inventory_reportes/resultado-de-romaneo-report/',
   r'^inventory_reserve/$',
   r'^inventory_reserve/add$',
   r'^inventory_reserve/(?P<pk>[0-9]+)/$',
   r'^inventory_reserve/inventory_filter_list$',
   r'^inventory_reserve/release_reserved_inventory$',

   
   # ------- New Entrance process ended ----------

   # ------- New Requirement Details -------------

   r'^media/*',
   )

