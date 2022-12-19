  $(document).on('blur', '.whm_boxes', function() {
    variable_weight = $(this).closest("tr").find(".w_product_measurment").find(":selected").attr("data-variable_weight")
    boxes = $(this).val()
    weight = $(this).closest("tr").find(".w_product_measurment").find(":selected").data("weight")
    total = parseFloat(boxes) * parseFloat(weight)

    existing_val = $(this).closest("tr").find(".whm_total_kg").val()
      existing_val = parseFloat(existing_val)
      if(existing_val > 0){
        if(variable_weight == 'false'){
          $(this).closest("tr").find(".whm_total_kg").val(total)
        }

      }
      else{
        $(this).closest("tr").find(".whm_total_kg").val(total)
      }
  })  
  $(".exit_product").select2()
  $(document).on('blur', '.price_calculation', function() {
    current_td = $(this)
    tr = current_td.closest('tr')
    calculate_row_price(tr)
    sum_table()
  });


 function check_print_picking(id) {
  
      jQuery.ajax({
              url: "/warehouse_exit/"+id+"/check-print-picking",
              type: "GET",
              dataType: "json"
            }).done(function( response ){
                print_picking = !response.data.print_picking
                // GGV
                $('.send_to_maneuvers').prop('disabled', print_picking)
                $('.print_picking').prop('disabled', print_picking)
                })
      
  }



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
  total_kg = tr.find('.whm_total_kg').val()
  price = tr.find('.whm_tprice').val()
  kg_per_price = tr.find('.whm_kg_per_price').val()
  boxes = tr.find('.whm_boxes').val()
  kg_per_boxes = tr.find('.whm_kg_per_boxes').val()

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

  tr.find(".whm_kg_per_price").val(result_price.toFixed(2))

  tr.find(".whm_kg_per_boxes").val(truncateToDecimals(result_boxes))

}

function truncateToDecimals(num, dec = 3) {
  const calcDec = Math.pow(10, dec);
  return Math.trunc(num * calcDec) / calcDec;
}

function sum_table(){
  result_total_kg = 0.0
  result_price = 0.0
  result_kg_per_price = 0.0
  result_boxes = 0.0
  result_kg_per_boxes = 0.0
  // alert("dfdfdf")
  $('.measurement_table .tr_body:visible').each(function(){
   
    total_kg = $(this).find(".whm_total_kg").val()
    price = $(this).find('.whm_tprice').val()
    kg_per_price = $(this).find('.whm_kg_per_price').val()
    boxes = $(this).find('.whm_boxes').val()
    kg_per_boxes = $(this).find('.whm_kg_per_boxes').val()

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
  $("#exit_total_kg").val(result_total_kg.toFixed(3))
  $("#exit_total_price").val(result_price.toFixed(2))
  $("#exit_kg_per_price").val(result_kg_per_price.toFixed(3))
  $("#exit_boxes").val(parseInt(result_boxes))
  $("#exit_kg_per_boxes").val(result_kg_per_boxes.toFixed(3))
}


$("[id$=image-clear_id]").css({'display': "none"})
$("[id$=image-clear_id]").next().css({'display': "none"})



exit_confirmation()
function exit_confirmation(){
  if($("#id_exit_match_invoice").is(":checked") == true){
    $(".confirm_exit").prop("disabled", false)
  }
  else{
    $(".confirm_exit").prop("disabled", true)
  }
}
$("#id_exit_match_invoice").click(function(){
  exit_confirmation()
}) 

$(".confirm_exit").click(function(){
      load_partial_product()
  })

var warehouse_locations =[];
function set_location(location_num, btn){
          $("#list_location").find('input').each(function(){
            $(this).removeAttr('style')
          })
          $(btn).css({"background": "#41f8ff none repeat scroll 0% 0%"})
          $("#exit_product_detail").find(".active_p").find("[id$='location']").val(location_num)
          var select = $("#exit_product_detail").find(".active_p").find("[id$='warehouse']")
          select.empty()
          warehouse_id = $("#warehouse_select_id option:selected").val()
          warehouse_text = $("#warehouse_select_id option:selected").text()
          select.append('<option selected="selected" value="'+warehouse_id+'">' +warehouse_text+'</option>')
          
          $("#exit_product_detail").find(".active_p").find("[id$='removed_boxes']").val("")
          $("#exit_product_detail").find(".active_p").find("[id$='removed_kgs']").val("")
          $("#exit_product_detail").find(".active_p").find("[id$='auto_pick_data']").text("")
        }



function set_location_and_rack(location_num, rack_number,weight,volume){
          $("#list_location").find('input').each(function(){
            $(this).removeAttr('style')
          })          

          weight_product = $("#exit_product_detail").find(".active_p").attr('data-available-weight')
          volume_product = $("#exit_product_detail").find(".active_p").attr('data-available-volume')

          // $(btn).css({"background": "#41f8ff none repeat scroll 0% 0%"})
          if(((parseFloat(weight)) >= (parseFloat(weight_product))) &&  ((parseFloat(volume)) >= (parseFloat(volume_product))) ){
            $("#exit_product_detail").find(".active_p").find("[id$='location']").val(location_num)
            var select = $("#exit_product_detail").find(".active_p").find("[id$='warehouse']")
            select.empty()
            warehouse_id = $("#warehouse_select_id option:selected").val()
            warehouse_text = $("#warehouse_select_id option:selected").text()
            select.append('<option selected="selected" value="'+warehouse_id+'">' +warehouse_text+'</option>')
            
            $("#exit_product_detail").find(".active_p").find("[id$='removed_boxes']").val("")
            $("#exit_product_detail").find(".active_p").find("[id$='removed_kgs']").val("")
            $("#exit_product_detail").find(".active_p").find("[id$='auto_pick_data']").text("")
            $("#calculate_total_weight").val('true')
          }
          else{
            $("#exit_product_detail").find(".active_p").find("[id$='location']").val('')
              $("#exit_product_detail").find(".active_p").find("[id$='rack_number']").val('')
              var select = $("#exit_product_detail").find(".active_p").find("[id$='warehouse']")
              select.empty()
            alert("La ubicación no cuenta con el espacio suficiente o el peso sobrepasa el limite del nivel de la ubicación. Por favor seleccione otra ubicación")
          }
        }

$(".partial_product").delegate('tr', 'click', function() {
      // var position = $(this).attr('data-row').replace ( /[^\d.]/g, '' );
      var position = $(this).attr('data-measurement');
      var position2  = $(".partial_product tr").length;
      
      var position1  = $("#exit_product_detail").find('.wexitconfirmation_set').length
      // var position1  = $(this).attr('data-row').replace ( /[^\d.]/g, '' );
      // console.log(position2,position1)
       $("#exit_product_detail").find('.wexitconfirmation_set').each(function(e){
        $(this).removeClass('active_p')
      })

      $(".partial_product tr").each(function(){
          $(this).removeClass('active_p')
      })

      weight = $(this).attr('data-available-weight')
      volume = $(this).attr('data-available-volume')
      
      $(this).addClass('active_p')
      var selector = $("#exit_product_detail").find('.wexitconfirmation_set[data-role="w_exit_confirmation_pallet_row_'+position+'"]')
      
      if(selector.length == 0){
          measurement_available = $(".measurement_"+position).length
          if(measurement_available > 0){
            exit_product_detail = $("#exit_product_detail").find(".measurement_"+position)
            exit_product_detail.addClass('active_p')
          }
            else{
            addConfirmProduct(true, position1)
          }        
        var selector = $("#exit_product_detail").find('.wexitconfirmation_set[data-role="w_exit_confirmation_pallet_row_'+position1+'"]')
      }
     
      selector.addClass('active_p')
      selector.removeClass('new_confr')
      selector.attr("data-available-weight",weight);
      selector.attr("data-available-volume",volume);
      selector.find("[id$='code']").val($(this).find(".product_code").text())
      selector.find("[id$='product']").empty()
      selector.find("[id$='product']").append('<option value="'+$(this).find(".product_id").val()+'">' +$(this).find(".product_description").text()+'</option>')
      

    });

function addPallet(total_pallete, selector, position_i) {
        position1 = selector.find('.exit_product').attr('name').replace ( /[^\d.]/g, '' )
        var existing_pallet_length = selector.find('.pallete_form_list').find(".row").length
        var count = 0
        var initial = 0
        var position = existing_pallet_length
        var existing_pallet = existing_pallet_length  
              
        total_pallete.forEach(function(palet){  
          per_boxes = parseInt($('.partial_product').find('.active_p').find('.kg_per_boxes').text()) 
          per_box =  parseFloat(palet.boxes* per_boxes).toFixed(3)          
          if(existing_pallet_length>0){
            
            var current_elm = selector.find('.pallete_form_list').find('.row:eq('+count+')')


            current_elm.find(".inventory_id").val(palet.inventory)
            current_elm.find(".inventory_gross_weight").val(palet.inventory_gross_weight)
            current_elm.find(".inventory_net_weight").val(palet.inventory_net_weight)
            current_elm.find(".rack_number").empty()
           current_elm.find(".rack_number").append($("<option></option>")
                   .attr("value",palet.rack_number,'class','selected')
                   .text(palet.rack_name));
           current_elm.find(".warehouse").empty()
           current_elm.find(".warehouse").append($("<option></option>")
                   .attr("value",palet.warehouse,'class','selected')
                   .text(palet.warehouse_name));
           current_elm.find(".location").empty()
           current_elm.find(".location").append($("<option></option>")
                   .attr("value",palet.location,'class','selected')
                   .text(palet.location_name));
           current_elm.find(".inventory").empty()
           current_elm.find(".inventory").append($("<option></option>")
                   .attr("value",palet.inventory,'class','selected')
                   .text(palet.inventory));

            current_elm.find("input[type=text]").prop('readonly', false)
            current_elm.find(".boxes").prop('readonly', true).val(palet.boxes)
            current_elm.find(".box_kg").prop('readonly', true).val(per_box)
            // current_elm.find(".box_kg").prop('readonly', true).val(palet.box_kg)
            current_elm.find(".palet_lot").prop('readonly', true).val(palet.pallet)
            
            // current_elm.find(".warehouse").prop('readonly', true).val(palet.warehouse)

            // current_elm.find(".rack_number").prop('readonly', true).val(palet.rack_number)
            // current_elm.find(".location").prop('readonly', true).val(palet.location)
            current_elm.find(".cost_lot").prop('readonly', true).val(palet.cost_lot)
            current_elm.find(".exp_date").prop('readonly', true).val(palet.exp_date)
            current_elm.find(".gross_weight").val(palet.gross_weight)
            current_elm.find(".net_weight").val(palet.net_weight)
            current_elm.find(".invoice_weight").prop('readonly', true).val(palet.invoice_weight)
            current_elm.find(".retained_quantity").attr('data-value',palet.retained_quantity)
            current_elm.find(".retained_reason").prop('readonly', true).val(palet.retained_reason)
            // current_elm.find(".inventory").prop('readonly', true).val(palet.inventory)
            current_elm.find("input[type=checkbox]").prop('checked', false)
            current_elm.removeClass("deleted-data")
            current_elm.find("select").prop('disabled', false)
            current_elm.find('.required-pallet').addClass('required-field')            
          }else{
            console.log(palet)
            
            selector.find('.pallete_form_list').append(selector.find('.empty_pallate_detail_form').html().replace(/__prefix__/g, count).replace(/__prefixe__/g, count).replace(/__position__/g, position_i).replace(/place_position/g, parseInt(count)+1));
            var current_elm = selector.find('.pallete_form_list').find('.row:eq('+count+')')
            
            current_elm.find(".inventory_id").val(palet.inventory)
            current_elm.find(".inventory_gross_weight").val(palet.inventory_gross_weight)
            current_elm.find(".inventory_net_weight").val(palet.inventory_net_weight)
            current_elm.find(".warehouse").find('option').addClass('hide')
            current_elm.find(".rack_number").find('option').addClass('hide')
            current_elm.find(".location").find('option').addClass('hide')

            current_elm.find(".boxes").prop('readonly', true).val(palet.boxes)
            current_elm.find(".box_kg").prop('readonly', true).val(per_box)
            // current_elm.find(".box_kg").prop('readonly', true).val(palet.box_kg)
            current_elm.find(".palet_lot").prop('readonly', true).val(palet.pallet)
            current_elm.find(".warehouse").prop('readonly', true).val(palet.warehouse)
            current_elm.find(".rack_number").prop('readonly', true).val(palet.rack_number)
            current_elm.find(".location").prop('readonly', true).val(palet.location)
            current_elm.find(".cost_lot").prop('readonly', true).val(palet.cost_lot)
            current_elm.find(".exp_date").prop('readonly', true).val(palet.exp_date)
            current_elm.find(".gross_weight").val(palet.gross_weight)
            current_elm.find(".net_weight").val(palet.net_weight)
            current_elm.find(".invoice_weight").prop('readonly', true).val(palet.invoice_weight)
            current_elm.find(".retained_quantity").attr('data-value',palet.retained_quantity)
            current_elm.find(".retained_reason").prop('readonly', true).val(palet.retained_reason)
            total_form = selector.find(".pallete_form_list").find("#id_pallete-wexitconfirmation_set-"+position1+"-warehouseexitpallet_set-TOTAL_FORMS").val()
            current_elm.find(".inventory").prop('readonly', true).val(palet.inventory)
           
            selector.find(".pallete_form_list").find("#id_pallete-wexitconfirmation_set-"+position1+"-warehouseexitpallet_set-TOTAL_FORMS").val(parseInt(total_form)+1)
            $('#id_pallete-wexitconfirmation_set-'+existing_pallet_length+'-warehouseexitpallet_set-'+count+'-exp_date')
            // .datepicker({
            //   autoclose: false,
            //   format: 'yyyy-mm-dd',
            // }).datepicker("setDate", new Date());            
          }
          count +=1
          existing_pallet_length -=1
          position +=1

        })
        
        while(existing_pallet-total_pallete.length > 0){
          existing_pallet -=1;
          var current_elml = selector.find('.pallete_form_list').find(".row:eq("+existing_pallet+")")
          // console.log(current_elml)
          current_elml.find("input[type=checkbox]").prop('checked', true)
          current_elml.find("input[type=text]").prop('readonly', true).val("")
          current_elml.find("select").prop('disabled', true).val("")
          current_elml.addClass("deleted-data")
          // console.log(existing_pallet,total_pallete.length)
          current_elml.find('.required-pallet').removeClass('required-field')
          // current_elml.find('select').removeClass('required-field')
        }        
              
       }

setInterval(function(){

  var error =  false
  $("#exit_product_detail").find(".wexitconfirmation_set").each(function(){
    $(this).find(".skip_validation").each(function(){  
      if($(this).val() == ''){
        error = true;
      }
    })                  
  })
  if(error){
    $(".print_picking").prop('disabled', true)
  }
  else{
    // GGV Disable the print picking button
    // $(".print_picking").removeAttr('disabled')
  }         
}, 100)

$(".automatic_picking").click(function(){

    div_data = $( "<div class='picking-loader-image'> <img src='/static/theme/img/loader.gif' alt='loader'/ ></div> " )
    $(".parent-loader").append(div_data) 
    selected = $(".partial_product .active_p")
    product_id = selected.find('.product_id').val()
    boxes = selected.find('.boxes').text()
    var position_conf = $(".wexitconfirmation_set.active_p").find('.peso_bruto').attr('name').replace ( /[^\d.]/g, '' )
    var w_conf_status=$("#id_wexitconfirmation_set-{0}-id".f(position_conf)).val()

    if ((product_id != '') && (parseFloat(boxes) >0)){
      get_auto_picking_data(product_id,boxes,w_conf_status)      
    }
    else{
      alert("Configurar mas de 0 cajas")
      $(".parent-loader").find(".picking-loader-image").fadeOut(1000, function(){ $(this).remove();});

    }

      
})

$(".entrance-filter").click(function(){
            div_data = $( "<div class='picking-loader-image'> <img src='/static/theme/img/loader.gif' alt='loader'/ ></div> " )
              $(".parent-loader").append(div_data)   
            selected = $(".partial_product .active_p")
            product_id = selected.find('.product_id').val()
            request_boxes = selected.find('.boxes').text()
            var position_conf = $(".wexitconfirmation_set.active_p").find('.peso_bruto').attr('name').replace ( /[^\d.]/g, '' )
             var w_conf_status=$("#id_wexitconfirmation_set-{0}-id".f(position_conf)).val()
            if ((product_id != '') && (parseFloat(request_boxes) >0)){
                  get_filter_picking_data(product_id,request_boxes,w_conf_status)
                }
                else{
                  alert("Configurar mas de 0 cajas")
                  $(".parent-loader").find(".picking-loader-image").fadeOut(1000, function(){ $(this).remove();});
                }
    })
function get_filter_picking_data(product_id,request_boxes,w_conf_status){
    
  jQuery.ajax( {
              url: "/warehouse_exit/exit_filter_for_location/",
              type: "POST",
              dataType: "json",
              data:{
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                
                werehouse_entrance_confirmation__werehouse_entrance_id: $('.folio_entrada').val(),
                werehouse_entrance_confirmation__werehouse_entrance__cust_reference: $('.referencia').val(),
                exp_date: $('.caducidad').val(),
                cost_lot: $('.lote_cliente').val(),
                palet_lot: $('.lote_tarima').val(),
                werehouse_entrance_confirmation__product_id: product_id,
                request_boxes: request_boxes

              }
          }
          ).done( function( response )

            {
              if(response.code == 200){

                  // var position = selected.attr('data-row').replace ( /[^\d.]/g, '' )
                 if(w_conf_status!=""){
                    var position = selected.attr('data-measurement')
                  }else{
                    // var position = selected.attr('data-row').replace ( /[^\d.]/g, '' )
                    var position = $(".wexitconfirmation_set.active_p").find('.peso_bruto').attr('name').replace ( /[^\d.]/g, '' )
                  }
                  var selector = $("#exit_product_detail").find('.wexitconfirmation_set[data-role="w_exit_confirmation_pallet_row_'+position+'"]')
                  
                  total_pallete= []
                  for (i = 0; i < response.responcedata.length; i++) {
                      total_pallete.push(response.responcedata[i])
                  }                  
                  // addPallet(total_pallete, selector, position)

                  if (selector.find('.empty_pallate_detail_form').length !=0 ){
                    addPallet(total_pallete, selector, position)
                  }
                  else{
                    alert("Necesidad de enviar los datos de confirmación primero.")
                  }
              }
              else{
                alert("No hay espacio para casillas solicitadas, Casillas disponibles es "+ response.boxes  +"")
              }
              $(".parent-loader").find(".picking-loader-image").fadeOut(1000, function(){ $(this).remove();});
         
            })
}
function get_auto_picking_data(product_id,boxes,w_conf_status){
    
  jQuery.ajax( {
              url: "/warehouse_exit/auto-picking",
              type: "POST",
              dataType: "json",
              data:{
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                request_boxes:  boxes,
                product: product_id,
                customer: $("#id_customer").val(),
              }
            } ).done( function( response )

            {
              console.log(response)
              if(response.code == 200){
                if(w_conf_status!=""){
                  var position = selected.attr('data-measurement')
                }else{
                  // var position = selected.attr('data-row').replace ( /[^\d.]/g, '' )
                  var position = $(".wexitconfirmation_set.active_p").find('.peso_bruto').attr('name').replace ( /[^\d.]/g, '' )
                }
                  
                  var selector = $("#exit_product_detail").find('.wexitconfirmation_set[data-role="w_exit_confirmation_pallet_row_'+position+'"]')
                  console.log(selector)
                  total_pallete= []
                  for (i = 0; i < response.responcedata.length; i++) {
                      total_pallete.push(response.responcedata[i])
                  }
                  if (selector.find('.empty_pallate_detail_form').length !=0 ){
                    addPallet(total_pallete, selector, position)
                    load_exit_box_data()
                  }
                  else{
                    // create_a_empty_pallet()
                    // addPallet(total_pallete, selector, position)
                    // $(".row wexitconfirmation_set .active_p").find('.empty-pallet-create').append(html.html())
                    
                    // alert("Necesidad de enviar los datos de confirmación primero.")
                  }
                  selector.find('.empty-pallet-create').html('')
                  // $("#empty_product_detail_form").html('')
                  
              }
              else{
                alert("No hay espacio para casillas solicitadas, Casillas disponibles es "+ response.boxes  +"")
              }
              $(".parent-loader").find(".picking-loader-image").fadeOut(1000, function(){ $(this).remove();});
         
            })
}
selected_option_show()


function create_a_empty_pallet(){
  html_section = "<div class='hide empty_pallate_detail_form'><div class='row col-xs-12 table-row'>  <div class='col-sm-2 form-group pallet_column'><input type='text' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-palet_lot' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-palet_lot' readonly='true' class='form-control palet_lot' maxlength='255'>  </div>  <div class='col-sm-2 form-group pallet_column'>  <input type='text' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-boxes' value='0' readonly='' class='form-control boxes required-field required-pallet' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-boxes'>  </div>  <div class='col-sm-2 form-group pallet_column'> <input type='text' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-warehouse' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-warehouse' readonly='true' class='form-control warehouse' maxlength='255'> </div>  <div class='col-sm-2 form-group pallet_column'> <input type='text' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-rack_number' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-rack_number' readonly='true' class='form-control rack_number' maxlength='255'> </div>    <div class='col-sm-2 form-group pallet_column'><input type='text' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-locatio' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-location' readonly='true' class='form-control location' maxlength='255'> </div>    <div class='col-sm-2 form-group pallet_column'>    <input type='text' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-cost_lot' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-cost_lot' class='form-control cost_lot required-field required-pallet' maxlength='255'>    </div>    <div class='col-sm-2 form-group pallet_column'>    <input type='text' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-exp_date' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-exp_date' class='form-control exp_date' maxlength='255'>    </div>    <div class='col-sm-2 form-group pallet_column'>      <input type='number' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-gross_weight' value='0.0' step='0.01' class='form-control gross_weight required-field required-pallet' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-gross_weight'>    </div>    <div class='col-sm-2 form-group pallet_column'>      <input type='number' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-net_weight' value='0.0' step='0.01' class='form-control net_weight required-field required-pallet' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-net_weight'>    </div>    <div class='col-sm-2 form-group pallet_column'>    <input type='number' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-invoice_weight' value='0' step='0.01' class='form-control invoice_weight required-field required-pallet' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-invoice_weight'>    </div>    <div class='col-sm-2 form-group pallet_column'>    <input type='number' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-retained_quantity' readonly='' data-value='' value='0' class='form-control retained_quantity required-field required-pallet' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-retained_quantity'>    </div>    <div class='col-sm-2 form-group pallet_column'>     <input type='text' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-retained_reason' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-retained_reason' class='form-control retained_reason' maxlength='255'>    </div>    <div class='col-sm-2 form-group pallet_column empty-block'>    <input type='hidden' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-werehouse_exit_confirmation' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-werehouse_exit_confirmation'>    </div>    <div class='col-sm-2 form-group pallet_column empty-block'>      <input type='hidden' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-id' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-id'>    </div>    <div class='col-sm-2 form-group pallet_column delete-block'>      <input type='checkbox' name='pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-DELETE' id='id_pallete-wexitconfirmation_set-__position__-warehouseexitpallet_set-__prefix__-DELETE'>    </div>    <div class='col-sm-2 form-group pallet_column'>      <a href='javascript:void(0)' class='btn btn-primary appDetails' style='margin-top: -25px;'>Mapa</a>    </div>    <a class='delete-row remove-form-row-pallet' href='javascript:void(0)'>X</a>  </div></div>"

  $("#exit_product_detail").find(".active_p").find('.empty-pallet-create').append(html_section)

}

function selected_option_show() {
  $("#exit_product_detail").find(".wexitconfirmation_set").each(function(index){
    if(($(this).find("[id$='warehouse']").val() != null) && ($(this).find("[id$='warehouse']").val().length > 0))
    {
      select = $(this).find("[id$='warehouse']").find('option').each(function(index){
        if(($(this)).attr('selected')!="selected"){
          $(this).addClass('hide')
        }
      })
    }

    if(($(this).find("[id$='rack_number']").val() != null) && ($(this).find("[id$='rack_number']").val().length > 0))
    {
      select = $(this).find("[id$='rack_number']").find('option').each(function(index){
        if(($(this)).attr('selected')!="selected"){
          $(this).addClass('hide')
        }
      })
    }

    if(($(this).find("[id$='location']").val() != null) && ($(this).find("[id$='location']").val().length > 0))
    {
      select = $(this).find("[id$='location']").find('option').each(function(index){
        if(($(this)).attr('selected')!="selected"){
          $(this).addClass('hide')
        }
      })
    }
    

  })
}

$(document).on('blur','.warehouse_retained_quantity', function() {
    $(this).parent().parent().find(".pallete_form_list").find(".retained_quantity").val($(this).val())
      column = $(this).closest(".wexitconfirmation_set")
      $(column).find('.retained_quantity').each(function(){
        retained_quantity_ele= $(this)
        compare_retained_quantity(retained_quantity_ele)
      })
      

  })

$(document).on('change','.retained_quantity',function(){
  
  retained_quantity_ele= $(this)
  compare_retained_quantity(retained_quantity_ele)

})

function compare_retained_quantity(retained_quantity_ele){
  var inventory_id = retained_quantity_ele.closest('.table-row').find('.inventory_id').val()
        var retained_quantity = retained_quantity_ele.attr('data-value')
        console.log(retained_quantity)
      jQuery.ajax({
              url: "/warehouse_exit/check_retained_quantity",
              type: "POST",
              dataType: "json",
              data:{
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                inventory_id:inventory_id,
                retained_quantity:retained_quantity,
              }
          }
          ).done( function( response ){
            if(response.code == 500){
              var entrance_retained_quantity = response.data.entrance_retained_quantity
              alert("Exit Pallet's retained qauntity should be less than or equal to "+ entrance_retained_quantity)
              retained_quantity_ele.val(0)
            }
          })
}


$(document).on('blur','.peso_neto', function() {
    $(this).parent().parent().find(".pallete_form_list").find(".net_weight").val($(this).val())
    $(this).parent().parent().find(".pallete_form_list").find(".net_weight").trigger("blur")
   column = $(this).closest(".wexitconfirmation_set")
   set_single_net_weight(column)
  })

$(document).on('blur','.peso_bruto', function() {
    $(this).parent().parent().find(".pallete_form_list").find(".gross_weight").val($(this).val())
    $(this).parent().parent().find(".pallete_form_list").find(".gross_weight").trigger("blur")
  column = $(this).closest(".wexitconfirmation_set")
  set_single_gross_weight(column)
  })


load_exit_box_data()
function load_exit_box_data(){
$(".wexitconfirmation_set").each(function(){
  set_single_boxes($(this))
  set_single_gross_weight($(this))
  set_single_net_weight($(this))
})
}

function set_single_boxes(column){
  total_box = 0
  box_length = $(column).find('.table-scroll .pallete_form_list .table-row .pallet_column').length
  $(column).find('.boxes').each(function(){

    if($(this).val()!=""){
      total_box+= parseInt($(this).val())
    }
    
  }) 

  $(column).find('.total_boxes').val(total_box)
  if(box_length >0){
    $(column).find(".table-row-total").removeClass('hide')
  }
  else{
    $(column).find(".table-row-total").addClass('hide')
  }
  
  
}

function set_single_gross_weight(column){
  total_box = 0
  $(column).find('.gross_weight').each(function(){
    if($(this).val()==''){
     $(this).val(0.0)
  }
    if($(this).val()!=""){
    total_box+= parseFloat($(this).val())
  }
  })
  $(column).find('.total_gross_weight').val(total_box)
}

function set_single_net_weight(column){
  total_box = 0
  $(column).find('.net_weight').each(function(){
    if($(this).val()==''){
     $(this).val(0.0)
  }
    if($(this).val()!=""){
    total_box+= parseFloat($(this).val())
  }
  })
  $(column).find('.total_net_weight').val(total_box)
}


$(document).on('click', '#save_maniover', function() {
  var data = []
  var zero_boxes = false
  var zero_total_kg = false
  $(".measurement_table").find(".tr_body").each(function(){
    tr_body = $(this)

    product_id = tr_body.find(".w_product_measurment").find(":selected").val()
    exp_date = tr_body.find(".exp_date").val()
    cost_lot = tr_body.find(".cost_lot").val()
    palet_lot = tr_body.find(".palet_lot").val()
    werehouse_entrance_id = tr_body.find(".werehouse_entrance").val()
    whm_boxes = tr_body.find(".whm_boxes").val()
    whm_total_kg = tr_body.find(".whm_total_kg").val()
    customer_id = $("#id_customer").find(":selected").val()
    if(parseInt(whm_boxes) == '0'){
      
      whm_boxes = 0
      zero_boxes = true
    }
    if(parseInt(whm_total_kg) == '0'){
      zero_total_kg = true
      whm_total_kg = 0
    }
    data.push({
      product_id: product_id, 
      exp_date:  exp_date,
      cost_lot: cost_lot,
      palet_lot: palet_lot,
      werehouse_entrance_id: werehouse_entrance_id,
      whm_boxes: whm_boxes,
      whm_total_kg: whm_total_kg,
      customer_id: customer_id
    });
  })

  if(zero_boxes == true){
    alert("El valor de las cajas no debe ser 0")
    return false
  }
  if(zero_total_kg == true){
    alert("El valor total de kg no debe ser 0")
    return false
  }
  jQuery.ajax({
    url: "/warehouse_exit/auto-print-picking",
    type: "POST",
    dataType: "json",
    data: {'data':JSON.stringify(data)},

  }).done(function( response ){
    success = true
    alert_json = []
     $(".entrance_error_on_maniobras").html("")
    response.data.forEach(function(data){
      if(data.status != 'true'){
        success = false
       
        $(".error_table").append("<tr><td>"+data.product_code+"</td><td>"+data.product_desc+"</td><td>"+data.boxes+"</td><td>"+data.request_boxes+"</td></tr>");
        
      }
    })
    if(success == true){
      $("#id_status").val('InManeuvers')
      $.LoadingOverlay("show");
      var xhr = new XMLHttpRequest();
      xhr.open("POST", ""); 
      xhr.responseType= 'blob';
      xhr.onload = function(event){ 
        $.LoadingOverlay("hide");
        var disposition = event.target.getResponseHeader('Content-Disposition');
        filename = "Picking_id"+".pdf"
        if (disposition && disposition.indexOf('attachment') !== -1) {
          var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
          var matches = filenameRegex.exec(disposition);
          if (matches != null && matches[1]) { 
            filename = matches[1].replace(/['"]/g, '');
          }
      }

        download_pdf(event.target.response, filename)

        $(window).off('beforeunload');
        window.location = '/warehouse_exit/new-warehouse-exit-list';
      };
      var formData = new FormData(document.getElementById("sga-form")); 
      xhr.send(formData);
    }
    else{
      $("#entrance_error_modal").modal("show")
    }
  })

});
