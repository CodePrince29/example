$('.product').select2()

$(document).on('blur', '.price_calculation', function() {
      current_td = $(this)
      tr = current_td.closest('tr')
      calculate_row_price(tr)
      sum_table()
    });

  $(document).on('change', '.whm_boxes', function() {
      current_td = $(this)
      tr = current_td.parent().parent()
      calculate_available_product_weight(tr)
    });


  function calculate_available_product_weight(tr) {
    boxes = tr.find('td:eq(5)').find("input").val()
    product = tr.find('td:eq(0)').find("option:selected")
    product_volume = product.attr('data-volume')
    product_weight = product.attr('data-weight')      
    available_volume = parseFloat(product_volume) * parseFloat(boxes)
    available_weight = parseFloat(product_weight) * parseFloat(boxes) 
    product.attr('data-available-weight', available_weight)
    product.attr('data-available-volume', available_volume)

  }



    function calculate_row_price(tr) {
    // tr = $(tr)
    total_kg = tr.find('td:eq(2)').find("input").val()
    price = tr.find('td:eq(3)').find("input").val()
    kg_per_price = tr.find('td:eq(4)').find("input").val()
    boxes = tr.find('td:eq(5)').find("input").val()
    kg_per_boxes = tr.find('td:eq(6)').find("input").val()

    total_kg = total_kg != '' ? parseFloat(total_kg) : 0
    price = price != '' ? parseFloat(price) : 0
    kg_per_price = kg_per_price != '' ? parseFloat(kg_per_price) : 0
    boxes = boxes != '' ? parseFloat(boxes) : 0
    kg_per_boxes = kg_per_boxes != '' ? parseFloat(kg_per_boxes) : 0

    result_price=0
    if (price>0) {
      result_price = (total_kg/price)
    }
    result_boxes=0
    if (boxes>0) {
      result_boxes = (total_kg/boxes)
    }
    // console.log(result_boxes)
    // console.log(truncateToDecimals(result_boxes))
    tr.find('td:eq(4)').find("input").val(result_price.toFixed(2))
    tr.find('td:eq(6)').find("input").val(truncateToDecimals(result_boxes))
    }

function truncateToDecimals(num, dec = 2) {
  const calcDec = Math.pow(10, dec);
  return Math.trunc(num * calcDec) / calcDec;
}
function sum_table(){
  result_total_kg = 0.0
  result_price = 0.0
  result_kg_per_price = 0.0
  result_boxes = 0.0
  result_kg_per_boxes = 0.0
  $('.measurement_table .tr_body:visible').each(function(){
    total_kg = $(this).find('td:eq(2)').find("input").val()
    price = $(this).find('td:eq(3)').find("input").val()
    kg_per_price = $(this).find('td:eq(4)').find("input").val()
    boxes = $(this).find('td:eq(5)').find("input").val()
    kg_per_boxes = $(this).find('td:eq(6)').find("input").val()


    total_kg1 = total_kg != '' ? parseFloat(total_kg) : 0.0
    price1 = price != '' ? parseFloat(price) : 0.0
    kg_per_price1 = kg_per_price != '' ? parseFloat(kg_per_price) : 0.0
    boxes1 = boxes != '' ? parseFloat(boxes) : 0.0
    kg_per_boxes1 = kg_per_boxes != '' ? parseFloat(kg_per_boxes) : 0.0

    result_total_kg+=total_kg1
    result_price+=price1
    result_kg_per_price+=kg_per_price1
    result_boxes+=boxes1
    result_kg_per_boxes+=kg_per_boxes1
  });

  $("#entrance_total_kg").val(result_total_kg.toFixed(2))
  $("#entrance_total_price").val(result_price.toFixed(2))
  $("#entrance_kg_per_price").val(result_kg_per_price.toFixed(2))
  $("#entrance_boxes").val(result_boxes.toFixed(2))
  $("#entrance_kg_per_boxes").val(result_kg_per_boxes.toFixed(2))
}

 
function set_location(location_num, btn){
          $("#list_location").find('input').each(function(){
            $(this).removeClass('active_p')
          })
          $(btn).addClass('active_p')
          $("#entrance_product_detail").find(".active_p").find("[id$='location']").val(location_num)
          var select = $("#entrance_product_detail").find(".active_p").find("[id$='warehouse']")
          select.empty()
          warehouse_id = $("#warehouse_select_id option:selected").val()
          warehouse_text = $("#warehouse_select_id option:selected").text()
          select.append('<option value="'+warehouse_id+'">' +warehouse_text+'</option>')

        }

function set_location_and_rack(location_num, rack_number,weight,volume){
          $("#list_location").find('input').each(function(){
            $(this).removeClass('active_p')
          })
          weight_product = $("#entrance_product_detail").find(".active_p").attr('data-available-weight')
          volume_product = $("#entrance_product_detail").find(".active_p").attr('data-available-volume')
          if(((parseFloat(weight)) >= (parseFloat(weight_product))) &&  ((parseFloat(volume)) >= (parseFloat(volume_product))) ){
              $("#entrance_product_detail").find(".active_p").find("[id$='location']").val(location_num)
              $("#entrance_product_detail").find(".active_p").find("[id$='rack_number']").val(rack_number)
              var select = $("#entrance_product_detail").find(".active_p").find("[id$='warehouse']")
              select.empty()
              warehouse_id = $("#warehouse_select_id option:selected").val()
              warehouse_text = $("#warehouse_select_id option:selected").text()
              select.append('<option value="'+warehouse_id+'">' +warehouse_text+'</option>')
              $("#calculate_total_weight").val('true')
          }else{
            // $("#entrance_product_detail").find(".active_p").find("[id$='location']").val('')
            //   $("#entrance_product_detail").find(".active_p").find("[id$='rack_number']").val('')
            //   var select = $("#entrance_product_detail").find(".active_p").find("[id$='warehouse']")
            //   select.empty()
            alert("La ubicaci??n no cuenta con el espacio suficiente o el peso sobrepasa el limite del nivel de la ubicaci??n. Por favor seleccione otra ubicaci??n")
          }
      }

  $(".confirm_entrance").click(function(){
      load_partial_product()
  })



$(".partial_product").delegate('tr', 'click', function() {
      var position = $(this).attr('data-measurement');
      var position2  = $(".partial_product tr").length;
      var position1  = $("#entrance_product_detail").find('.warehouseentranceconfirmation_set').length
      
       $("#entrance_product_detail").find('.warehouseentranceconfirmation_set').each(function(){
        $(this).removeClass('active_p')
      })

      $(".partial_product tr").each(function(){
          $(this).removeClass('active_p')
      })
      weight = $(this).attr('data-available-weight')
      volume = $(this).attr('data-available-volume')
      data_table_row = $(this).attr('data-table-row')

      $(this).addClass('active_p')
      var selector = $("#entrance_product_detail").find('.warehouseentranceconfirmation_set[data-role="w_entrance_confirmation_pallet_row_'+position+'"]')
      
      if(selector.length == 0){
        measurement_available = $(".measurement_"+position).length
          if(measurement_available > 0){
            entrance_product_detail = $("#entrance_product_detail").find(".measurement_"+position)
            entrance_product_detail.addClass('active_p')
          }
            else{
            addConfirmProduct(true, position1)
          } 
        var selector = $("#entrance_product_detail").find('.warehouseentranceconfirmation_set[data-role="w_entrance_confirmation_pallet_row_'+position1+'"]')
      }
      selector.addClass('active_p')
      
      selector.attr("data-available-weight",weight);
      selector.attr("data-table-row",data_table_row);
      selector.attr("data-available-volume",volume);
      product_code = $(this).find(".product_code").text()
      selector.find("[id$='code']").val($(this).find(".product_code").text())
      selector.find("[id$='product']").empty()
      selector.find("[id$='product']").append('<option value="'+$(this).find(".product_id").val()+'">' +$(this).find(".product_description").text()+'</option>')
      var pallet = parseInt($(this).find('.product_pallet').val())
      var boxes = parseInt($(this).find('.boxes').text())   
      data = []
      total_palet = parseInt((boxes/pallet))
      remain_palet = (boxes%pallet)
      total_pallete= []

      for (i = 0; i < total_palet; i++) {
          total_pallete.push(pallet) 
      }

      if(remain_palet > 0){
         total_pallete.push(remain_palet)
      }
      console.log(pallet,boxes)
      if((parseFloat(pallet) > 0) && (parseFloat(boxes) > 0)){
        addPallet(total_pallete, selector, position)
      }
      else{
        alert("Informaci??n Incompleta del producto:" + product_code)
      }
      load_count_boxes()
      
  });

  $(".warehouseentranceconfirmation_set .net_weight").on("change", function(){
    $(this).parent().parent().find(".pallete_form_list").find(".net_weight").val($(this).val())
  })

  $(".warehouseentranceconfirmation_set .gross_weight").on("change", function(){
    $(this).parent().parent().find(".pallete_form_list").find(".gross_weight").val($(this).val())
  })

  $(".warehouseentranceconfirmation_set .invoice_weight").on("change", function(){
    $(this).parent().parent().find(".pallete_form_list").find(".invoice_weight").val($(this).val())
  })


  $(".warehouseentranceconfirmation_set .retained_quantity").on("change", function(){
    box_value = $(this).parent().parent().find(".pallete_form_list").find('.boxes').val()
    console.log(box_value)
    if(box_value < $(this).val()){
      alert("Qauntity retenida no debe ser mayor que la cantidad de caja")
      $(this).parent().parent().find(".pallete_form_list").find(".retained_quantity").val(0)
      $(this).val(0)
    }else{
      $(this).parent().parent().find(".pallete_form_list").find(".retained_quantity").val($(this).val())
    }
    
  })


  $(".warehouseentranceconfirmation_set .retained_reason").on("change", function(){
    $(this).parent().parent().find(".pallete_form_list").find(".retained_reason").val($(this).val())
  })


  $(".warehouseentranceconfirmation_set .exp_date").on("change", function(){
    $(this).parent().parent().find(".pallete_form_list").find(".exp_date").val($(this).val())
  })


  $(".warehouseentranceconfirmation_set .cost_lot").on("change", function(){
    $(this).parent().parent().find(".pallete_form_list").find(".cost_lot").val($(this).val())
  })

function set_new_suto_value(selector, current_elm){
  current_elm.find(".net_weight").val(selector.find(".net_weight").val())

  current_elm.find(".gross_weight").val(selector.find(".gross_weight").val())

  current_elm.find(".invoice_weight").val(selector.find(".invoice_weight").val())


  current_elm.find(".retained_quantity").val(selector.find(".retained_quantity").val())


  current_elm.find(".retained_reason").val(selector.find(".retained_reason").val())


  current_elm.find(".exp_date").val(selector.find(".exp_date").val())


  current_elm.find(".cost_lot").val(selector.find(".cost_lot").val())
}


function addPallet(total_pallete, selector, position_i) {
   position1 = selector.find('.gross_weight').attr('name').replace ( /[^\d.]/g, '' )
        var existing_pallet_length = selector.find('.pallete_form_list').find(".row").length
        var count = 0
        var initial = 0
        var position = existing_pallet_length
        var existing_pallet = existing_pallet_length
        var kg_per_box = parseFloat($(".partial_product").find("tr.active_p").find(".kg_per_boxes").text())
        total_pallete.forEach(function(val){
          
          if(existing_pallet_length>0){
            var current_elm = selector.find('.pallete_form_list').find('.row:eq('+count+')')
            current_elm.find("input[type=checkbox]").prop('checked', false)
            current_elm.removeClass("deleted-data")
            current_elm.find("select").prop('disabled', false)
            current_elm.find('.required-pallet').addClass('required-field')
            current_elm.find(".boxes").val(val)
            box_kg_value = parseFloat(kg_per_box*val).toFixed(2)
            current_elm.find(".box_kg").prop('readonly', true).val(box_kg_value)
          }else{
            selector.find('.pallete_form_list').append(selector.find('.empty_pallate_detail_form').html().replace(/__prefix__/g, count).replace(/__prefixe__/g, count).replace(/__position__/g, position_i).replace(/place_position/g, parseInt(count)+1));
            var current_elm = selector.find('.pallete_form_list').find('.row:eq('+count+')')
            current_elm.find(".boxes").prop('readonly', true).val(val)
            box_kg_value = parseFloat(kg_per_box*val).toFixed(2)
            current_elm.find(".box_kg").prop('readonly', true).val(box_kg_value)
            total_form = selector.find(".pallete_form_list").find("#id_pallete-warehouseentranceconfirmation_set-"+position1+"-warehouseentrancepallet_set-TOTAL_FORMS").val()
            selector.find(".pallete_form_list").find("#id_pallete-warehouseentranceconfirmation_set-"+position1+"-warehouseentrancepallet_set-TOTAL_FORMS").val(parseInt(total_form)+1)
            $('#id_pallete-warehouseentranceconfirmation_set-'+existing_pallet_length+'-warehouseentrancepallet_set-'+count+'-exp_date').datepicker({
              autoclose: false,
              format: 'yyyy-mm-dd',
            }).datepicker("setDate", new Date());
            set_new_suto_value(selector, current_elm)
          }
          count +=1
          existing_pallet_length -=1
          position +=1

        })
        while(existing_pallet-total_pallete.length > 0){
          existing_pallet -=1;
          var current_elml = selector.find('.pallete_form_list').find(".row:eq("+existing_pallet+")")
       
          current_elml.find("input[type=checkbox]").prop('checked', true)
          current_elml.find("input[type=text]").prop('readonly', true).val("")
          current_elml.find("select").prop('disabled', true).val("")
          current_elml.addClass("deleted-data")          
          current_elml.find('.required-pallet').removeClass('required-field')
          current_elml.find('.exp_date').removeClass('required-field')
        }        
              
       }


$(document).on('change', ".warehouse", function() {
  warehouse = $(this).val()
  rack_column = $(this).parent().next().find('.rack_number')
  if(warehouse != '')
  {   
    $.LoadingOverlay('show')
    jQuery.ajax( {
      url: "/warehouse_entrance/get-rack/"+warehouse,
      type: "GET",
      dataType: "json",
    } ).done( function( response )
    {
      selected = rack_column.find(':selected').val()
      rack_column.empty()
      rack_column.append('<option value="" selected="selected">---------</option>')
      rack_data = response.racks

      rack_data.forEach(function(rack) {
          if(parseInt(selected) == parseInt(rack['id'])){
            rack_column.append('<option value="'+rack['id']+'" selected="selected">' +rack['index']+'</option>')  
          }
          else{
            rack_column.append('<option value="'+rack['id']+'">' +rack['index']+'</option>')
          }
      })
      $.LoadingOverlay('hide')
    }).error(function(resp){ console.log(resp); $.LoadingOverlay('hide')})
  }

})

$(document).on('change', ".rack_number", function() {
  rack_number = $(this).val()
  warehouse = $(this).parent().prev().find('.warehouse').find(':selected').val()
  location_column = $(this).parent().next().find('.location')
  var total_boxes = $(this).closest('.table-scroll').find('.total_boxes').val()
  var product_net_weight = $(".partial_product").find(".active_p").find(".product_net_weight").val()

  if(rack_number != '' && warehouse !=null )
  {
    $.LoadingOverlay('show')
    jQuery.ajax( {
      url: "/warehouse_entrance/get-location/",
      type: "POST",
      dataType: "json",
      data: { 
        warehouse: warehouse ,
        rack: rack_number ,
        total_boxes: total_boxes ,
        product_net_weight: product_net_weight
        }
    } ).done( function( response )
    {
      selected = location_column.find(':selected').val()
      location_column.empty()
      location_column.append('<option value="" selected="selected">---------</option>')
      response.locations.forEach(function(location) {
          if(parseInt(selected) == parseInt(location['id'])){
            location_column.append('<option value="'+location['id']+'" selected="selected">' +location['location_number']+'</option>')  
          }
          else{
            location_column.append('<option value="'+location['id']+'">' +location['location_number']+'</option>')
          }
      })
      if(response.locations.length == 0 ){
        alert("La secci??n seleccionada no tiene ninguna ubicaci??n que cumpla con los requisitos.")
      }
      $.LoadingOverlay('hide')
    }).error(function(resp){ console.log(resp); $.LoadingOverlay('hide')})
  }

})

// validate boxes

$(document).on('change', ".location", function() {
  var locs = $(this)
  var location = $(this).val()
  var warehouse = $(this).parent().prev().prev().find('.warehouse').find(':selected').val()
  var product_id  = $(".partial_product").find(".active_p").find(".product_id").val()
  var product_net_weight = $(".partial_product").find(".active_p").find(".product_net_weight").val()
  var total_boxes = $(this).closest('.table-scroll').find('.total_boxes').val()
  console.log(product_net_weight)
  if (warehouse != "" && total_boxes != "" && location != "" && product_id != ""){
    $.LoadingOverlay('show')
    jQuery.ajax( {
      url: "/warehouse_entrance/check-boxes-availability",
      type: "POST",
      dataType: "json",
      data: { 
        data: JSON.stringify({
          warehouse: warehouse ,
          location: location ,
          total_boxes: total_boxes ,
          product_net_weight: product_net_weight})}
    } ).done( function( response )
    {  
    $.LoadingOverlay('hide')   
     if(response.code != 200){
        locs.val('')
        alert("La ubicaci??n no cuenta con el espacio suficiente o el peso sobrepasa el limite del nivel de la ubicaci??n. Por favor seleccione otra ubicaci??n")
       
     }
    }).error(function(resp){ console.log(resp); $.LoadingOverlay('hide')})

  }
  else{
    alert("Por favor seleccione producto")
    $(this).val('')
  }
})

// Peso variable save
$(document).on("click",".romaneo_submit", function () {
  box_peso_veriable = $(this).parent().parent()
  pallet_id = box_peso_veriable.find(".romaneo_pallet_id").val()
  total_peso_variable = box_peso_veriable.find(".romaneo_peso_variable")
  peso_variable_data = []
  total_peso_variable.each(function(){
    peso_variable_data.push({
      "peso_variable_quantity": $(this).val(),
      "id": $(this).attr('data-peso-variable'),
      "werehouse_entrance_pallet": pallet_id
    }) 
  })
  $.ajax({
          url: "/warehouse_entrance/save-romaneo-peso-variables/"+pallet_id.toString(),
          type: "POST",
          dataType: "json",
          data: {'data':JSON.stringify(peso_variable_data)},
           
      }).done( function( response )
      { console.log(response)
          
          if(response.code == 200){
            Swal.fire('Romaneo Peso Variable',response.message,'success')
          }else{
            Swal.fire('Romaneo Peso Variable',response.message,'info')
          }
          $romaneo_row.find('.gross_weight').val(box_peso_veriable.find('.romaneo_peso_bruto').val())
          $romaneo_row.find('.net_weight').val(box_peso_veriable.find('.romaneo_peso_neto').val())
          $("#pallet_romaneo").modal('hide')
          $("#pallet_romaneo").find('input').val('')

      })
})

$(".send_to_maneuvers").click(function(){
  var active_total_kgs = 0
  var product_total_weight = 0
  var total_pallet_ids = []
  var total_loop = 0
  $(".partial_product tr").each(function(){
    var pallet_ids = []
    var active_total_kg = $(this).find('.total_kg').text()
    active_total_kgs+=parseInt(active_total_kg)
    $('div[data-role="w_entrance_confirmation_pallet_row_'+$(this).attr('data-measurement')+'"] .table-row').each(function(){
        var id_pallet = $(this).find('.id-pallet').find('input').val()
        if(id_pallet !== undefined){
          pallet_ids.push(id_pallet)
          total_pallet_ids.push(id_pallet)
        }
        
    })
    // Make api call to check variable quantity
    $.post("/warehouse_entrance/check-peso-variables-quantity", {'data':JSON.stringify(pallet_ids)}, function(response, status){
      console.log(response, status)
      product_total_weight += response.data.total_quantity
      total_loop+=1
    })
  })
  console.log(product_total_weight)
  var loopInt=setInterval(function(){
    if(total_loop == $(".partial_product tr").length){
      clearInterval(loopInt);
      if(product_total_weight >0 && active_total_kgs != product_total_weight){
      var question = 'El peso del romaneo: '+product_total_weight+' es diferente al peso esperado del producto: '+active_total_kgs+', Desea utilizar el peso del romaneo en lugar del peso del producto?';
      var confirmModal = $('#modal-romaneo-confirm')
      confirmModal.modal('show')
      confirmModal.find('.sure-confirmation').find('p').text(question)
      confirmModal.find('#romaneo-yes').unbind().click(function(event) {
          $.post("/warehouse_entrance/save-romaneo-weights", {pallet_ids: JSON.stringify(total_pallet_ids)},function( response , status)
              {
                confirmModal.modal('hide')
                $("#id_status").val("InManeuvers")
                $("#sga-form" ).submit()
              })

      });

      confirmModal.find('#romaneo-No').unbind().click(function(event) {
         confirmModal.modal('hide')
      });

    }
    else
      {
        $("#id_status").val("InManeuvers")
        $("#sga-form" ).submit()
      }
    }
  },200)
})
