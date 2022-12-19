$.ajax({
          url: '/warehouses/branches',
          type: "GET",
          dataType: "json",
          
    }).done( function( response ){
      var str = "<option value=''>------</option>"
      response.branches.forEach(function(branch){
        str +="<option value='"+branch.id+"'>"+branch.name+"</option>"
      })
      $("#id_warehouse_branch").append(str);
  })

  $("#id_time_branch").click(function(){
    $('#entrance_hours').val('')
    $('#exit_hours').val('')
    var date = $("#entrance_date").val()
    if(date == undefined){
      date = $("#exit_date").val()
    }
    $.ajax({
          url: '/warehouses/bays?date='+date+'&branch='+$("#id_warehouse_branch").val(),
          type: "GET",
          dataType: "json",
          
    }).done( function( response ){
      allowed_bays = response.data.allowed_bays;
      console.log(response)
      time_slots = "<table class='table'><tr><th>Hora de Llegada</th><th colspan='6'>Anden Disponible </th></tr><tr><td></td>"
      for(i=1; i<=allowed_bays; i++){
        time_slots+="<td><b>"+i+"</b></td>"
      }
      time_slots+="</tr>";
      let reservations = response.data.reservations;
      response.data.time_slots.forEach(function(t){
          time_slots+="<tr><td>"+t+"</td>"
          for(b=1; b<=allowed_bays; b++){
            loading = false
            reservations.forEach(function(r){
              if(r.bay == b && t === r.time){
                loading = r.loading
              }
            })
            if(loading){
              time_slots+="<td><input type='button' class='time_slots btn btn-danger' value='&nbsp;&nbsp;&nbsp;' data-time='"+t+"' data-bay='"+b+"' title='Reserved' disabled></td>"
            }
            else{
              time_slots+="<td><input type='button' class='time_slots btn btn-default' value='&nbsp;&nbsp;&nbsp;' data-time='"+t+"' data-bay='"+b+"' title='Vacant'></td>"
            }
          }
          time_slots+="</tr>"
      })
      time_slots+="</table>"
      $('#time_slot_modal').find('.bays-table').empty()
      $('#time_slot_modal').find('.bays-table').append(time_slots);
      
    })
    
  })

  $(document).on('click', '.time_slots',function(){
        $('#entrance_hours').val($(this).attr('data-time'))
        $('#exit_hours').val($(this).attr('data-time'))
        $('#bay_id').val($(this).attr('data-bay'))
        $('#branch_id').val($("#id_warehouse_branch").val())
        $(document).find('.time_slots').each(function(){
          $(this).attr('title', 'Vacant')
          $(this).removeClass('btn-info').removeClass('btn-default').addClass('btn-default');
        })
        $(this).attr('title', 'Reserved')
        $(this).toggleClass('btn-default');
        $(this).toggleClass('btn-info');
    });

  $("#id_time_slots").click(function(){
    if($('#exit_date').val() == undefined){
      $("#selected_date_id").text($("#entrance_date").val())
    }
    else {
      $("#selected_date_id").text($("#exit_date").val())
    }
    
    $("#time_slot_modal").modal('show')
  })
  $("#close_time_slot_modal").click(function(){
    $("#time_slot_modal").modal('hide')
  })

  $("#entrance_date").change(function(){
    $("#id_warehouse_branch").val('')
    $('#time_slot_modal').find('.bays-table').empty()
    $('#entrance_hours').val('')
  })

  $("#exit_date").change(function(){
    $("#id_warehouse_branch").val('')
    $('#time_slot_modal').find('.bays-table').empty()
    $('#exit_hours').val('')
  })