
$('.filter_expiry_date').datepicker({
	autoclose: false,
	format: 'yyyy-mm-dd',
})
$("#id_filter_customer").change(function(){
	if ($(this).val() != "") {
		customer_product()
	}
	
})

function customer_product() {
	jQuery.ajax( {
		url: "/warehouse_entrance/customer-products/"+$("#id_filter_customer").val(),
		type: "GET",
		dataType: "json",
	} ).done( function( response ) {
		products = response
		prod_select = $("#id_filter_product")
		selected = prod_select.val()
		prod_select = prod_select.empty()
		prod_select.append('<option value="" selected="selected">---------</option>')
		
		products.forEach(function(product) {
			if(selected == product['id']){
				prod_select.append('<option value="'+product['id']+'selected="selected">' +product['product_description']+'</option>')  
           }                         
			else{
				prod_select.append('<option value="'+product['id']+'">' +product['product_description']+'</option>')  

			}
		})
	})
}
	$(document).on("click",".row_filter", function (){		
		clicked_row = $(this)
		$(".row_filter").removeClass('row_selected')
		$(this).addClass('row_selected')
		$("#id_palet_lot").val(clicked_row.attr('data-lote_tarima'))
		$("#id_inventory").val(clicked_row.attr('data-inventory'))
		$("#id_boxes").val(clicked_row.attr('data-total_boxes'))
	})
	$("#id_reserve_boxes").blur(function(){
		boxes = parseFloat($("#id_boxes").val())
		reserve_boxes = parseFloat($(this).val())
		if (reserve_boxes > boxes) {
			alert("Cajas a Reservar debe ser menor que Cajas")
			$(this).val(boxes)			
		}else{
			$("#id_released_store_box").val($(this).val())
		}
	})

	$(document).on("click","#inventory_search_submit", function () {
		customer = $("#id_filter_customer").val()
		product = $("#id_filter_product").val()
		lote_tarima = $(".filter_lote_tarima").val()
		lote_cliente = $(".filter_lote_cliente").val()
		expiry_date = $(".filter_expiry_date").val()
		array = []
		if ((customer != '') || (product != '') || (lote_tarima != '') || (lote_cliente != '') || (expiry_date != '') ) {
			jQuery.ajax({
				url: "inventory_filter_list",
				type: "POST",
				dataType: "json",
				data: {
					customer: customer,
					product: product,
					lote_tarima: lote_tarima,
					lote_cliente: lote_cliente,
					expiry_date: expiry_date,
				}
			} ).done( function( response )
			{				
				$('table tbody').empty()
				if (response["code"] == "200") {
					
					response.filter_inventory.forEach(function(element) {
						row = "<tr class='row_filter' data-inventory="+ element.id +" data-lote_tarima="+ element.lote_tarima +" data-total_boxes="+ element.total_boxes +" >\
						<td>"+element.client_name+"</td>\
						<td>"+element.product_name+"</td>\
						<td>"+element.warehouse_name+"</td>\
						<td>"+element.rack+"</td>\
						<td>"+element.location_number+"</td>\
						<td>"+element.lote_tarima+"</td>\
						<td>"+element.lote_cliente+"</td>\
						<td>"+element.exp_date+"</td>\
						<td>"+element.peso_bruto+"</td>\
						<td>"+element.peso_neto+"</td>\
						</tr>"
						$('table tbody').append(row)
					})
				}
				else{
					alert("Registro no encontrado")
				}

			})
		}else{
			alert("Seleccione al menos una opción de filtro")
		}
	})



	$("form").validate({
	    rules: {      
	      palet_lot: "required",
	      boxes: "required",
	      reserve_boxes: "required",
	      motive_to_reserve: "required",      
	    },    
	    messages: {
	      palet_lot: "Lote Tarima requerido",
	      boxes: "Cajas requerido",
	      reserve_boxes: "Cajas a Reservar requerido",
	      motive_to_reserve: "Motivo a Reservar requerido",      
	    },
	   
	    submitHandler: function(form) {
	      form.submit();
	    }
	  });

