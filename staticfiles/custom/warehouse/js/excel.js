   $('#export_excel').on('click', function(){
      // simplify data
      $.LoadingOverlay('show',{'text': 'Exportador'})
      let timestamp = Math.floor(Date.now() / 1000)
       
      filename= "Movimientos_Historicos_"+timestamp.toString()+".xlsx";
      $("#datatable tbody").empty()
      let tableData = window.state.map(function(row){ return "<tr>"+row.slice(0,6).map(function(td){ return "<td>"+td+"</td>" }).join('')+"</tr>" }).join('')
      $("#datatable tbody").append(tableData)
      TableToExcel.convert(document.getElementById("datatable"), {
        name: filename,
        sheet: {
          name: "Movimientos Historicos"
        }
      })

      $.LoadingOverlay('hide')
      $("#datatable tbody").empty()
   })