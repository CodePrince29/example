   $('#export_excel').on('click', function(){
      // simplify data
      $.LoadingOverlay('show',{'text': 'Exportador'})
      let timestamp = Math.floor(Date.now() / 1000)
       
      filename= "Movimientos_Historicos_"+timestamp.toString()+".xlsx";

      TableToExcel.convert(document.getElementById("data-table"), {
        name: filename,
        sheet: {
          name: "Movimientos Historicos"
        }
      })

      $.LoadingOverlay('hide')
   })