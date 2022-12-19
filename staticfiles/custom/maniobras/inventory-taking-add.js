function checkStartsWith(str, prefix){
  return str.indexOf(prefix) === 0;
}

function checkDecimal(evt, item, lenBeforeDecimal, lenAfterDecimal) {
  var charCode = evt.which;
 
  var trimmed = $(item).val().replace(/\b^0+/g, "");
  if(checkStartsWith(trimmed, '.') == true){
    trimmed = '0' + trimmed;
  }  
  
  if(charCode == 8 || charCode == 9){
    return true;
  } 

  if(charCode == 46){
    var dotOccurrences = (trimmed.match(/\./g) || []).length;
    
    if(dotOccurrences != undefined && dotOccurrences == 1){
      return false;
    }else{
      return true;
    }
  }
  
  if (charCode > 31 && ((charCode < 48) || (charCode > 57))) {
    return false;
  }
    if ($(item).val() != trimmed){
        $(item).val(trimmed);}  
  
  if(trimmed.indexOf('.') == -1){
    if(trimmed.length >= parseInt(lenBeforeDecimal)){
      return false;
    }
  }else{
    var inputArr = trimmed.split(".");
    if(inputArr[1].length > 1 && charCode != 13){
      console.log("Hii")
      $(item).val(0)
    }
  }
  
  return true;
}

var dataTable = $("#data-pallet-list").DataTable({
                "columnDefs": [ {
          "targets": 11,
          "orderable": false
          },
          {
          "targets": 12,
          "orderable": false
          } ],

        "language": {
            "sProcessing":     "Procesando...",
            "sLengthMenu":     "Mostrar _MENU_ registros",
            "sZeroRecords":    "No se encontraron resultados",
            "sEmptyTable":     "Ningún dato disponible en esta tabla",
            "sInfo":           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0 registros",
            "sInfoFiltered":   "(filtrado de un total de _MAX_ registros)",
            "sInfoPostFix":    "",
            "sSearch":         "Buscar:",
            "sUrl":            "",
            "sInfoThousands":  ",",
            "sLoadingRecords": "Cargando...",
            "oPaginate": {
                "sFirst":    "Primero",
                "sLast":     "Último",
                "sNext":     "Siguiente",
                "sPrevious": "Anterior"
            },
            "oAria": {
                "sSortAscending":  ": Activar para ordenar la columna de manera ascendente",
                "sSortDescending": ": Activar para ordenar la columna de manera descendente"
            }
        }
    });


$("#update_pallet_info").click(function(){
        var modal = $(this).closest('.modal')
        data_row = []
        modal.find(".data-table tbody tr").each(function(v){ data_row.push($(this).find('td').map(function(){ return $(this).html() }).get() ) })
        if(data_row.length > 0){
          dataTable.rows.add(data_row).draw();
          dataTable.order([1, 'asc']).draw();
          dataTable.page('last').draw(false);
        }
        $("#scan_modal").modal("hide")
      })

  $("#id_filter_product").select2();

  $("#id_filter_customers").change(function(){
    if ($(this).val() != "") {
      customer_product()
    }

  })
  function customer_product() {
    product_ids =[]
    jQuery.ajax( {
      url: "/warehouse_entrance/customer-products/"+$("#id_filter_customers").val(),
      type: "GET",
      dataType: "json",
    } ).done( function( response ) {
      products = response
      prod_select = $("#id_filter_product")
      selected = prod_select.val()
      prod_select = prod_select.empty()
      prod_select.append('<option value="ALL">Todas</option>')

      products.forEach(function(product) {
        product_ids.push(product['id'])
        if(selected == product['id']){
          prod_select.append('<option value="'+product['id']+'selected="selected">' + product['product_code']+" " + product['product_description']+'</option>')
        }
        else{
          prod_select.append('<option value="'+product['id']+'">' + product['product_code'] + " " +product['product_description']+'</option>')  

        }
      })
    })
  }

$(document).on('click', '.remove_record', function() {
    palet = $(this).attr('data-palet-id')
    product = $(this).attr('data-product-id')
    if ((palet !="") && (product!="")) {
      scanned_palet_ids.splice($.inArray(parseInt(palet), scanned_palet_ids),1);
      scanned_product_ids.splice($.inArray(parseInt(product), scanned_product_ids),1);
      $(this).closest("tr").remove();
    }
    else{
      alert("No se puede eliminar la fila seleccionada")
    }
  })

$(document).on('keyup', ".inv_total_boxes", function(){
    var available_total_boxes = parseInt($("#data-pallet-list").find('tr.active_p').find('.available_total_boxes').text())
    if(available_total_boxes > parseInt($(this).val())){
      $('.save_observation').prop('disabled', true)
    }else{
      $('.save_observation').prop('disabled', false)
    }
  })

$(document).on('keyup', "#total_kg", function(){
    if( parseInt($(this).val()) < 0){
      $('.save_observation').prop('disabled', true)
    }else{
      $('.save_observation').prop('disabled', false)
    }
  })

$(document).on("click",".romaneo_cancel", function () {
        $("#pallet_romaneo").modal('hide')
    })